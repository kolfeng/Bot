import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
HUGGINGFACE_TOKEN = os.environ.get('HUGGINGFACE_API_KEY')

class AIChatBot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.model_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    
    def get_ai_response(self, message):
        """Получаем ответ от нейросети"""
        try:
            payload = {
                "inputs": message,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.9,
                    "do_sample": True,
                    "top_p": 0.95,
                    "repetition_penalty": 1.1
                }
            }
            
            response = requests.post(
                self.model_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', 'Не удалось сгенерировать ответ')
                return "Получен пустой ответ"
                
            elif response.status_code == 503:
                return "🔄 Модель загружается... Пожалуйста, подождите 20-30 секунд и попробуйте снова."
                
            else:
                return f"❌ Ошибка API (код {response.status_code}). Попробуйте позже."
                
        except requests.exceptions.Timeout:
            return "⏰ Таймаут запроса. Попробуйте еще раз."
        except Exception as e:
            logger.error(f"Error: {e}")
            return "⚠️ Произошла ошибка при обработке запроса."

# Создаем экземпляр бота
ai_bot = AIChatBot(HUGGINGFACE_TOKEN)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
🤖 **Привет! Я AI-бот на основе нейросети**

Используется модель: **Microsoft DialoGPT-medium**

Просто напиши мне сообщение, и я постараюсь дать осмысленный ответ!

⚡ **Технологии:**
• Telegram Bot API
• Hugging Face Inference API
• Microsoft DialoGPT-medium
• Render.com
    """
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📖 **Доступные команды:**
/start - начать работу
/help - показать эту справку

💡 **Просто напиши любое сообщение** и получи ответ от AI!
    """
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_message = update.message.text
    
    # Показываем статус "печатает"
    await update.message.chat.send_action(action="typing")
    
    # Получаем ответ от нейросети
    bot_response = ai_bot.get_ai_response(user_message)
    
    # Отправляем ответ
    await update.message.reply_text(bot_response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    if update.message:
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")

def main():
    """Основная функция"""
    # Проверяем наличие токенов
    if not TELEGRAM_TOKEN or not HUGGINGFACE_TOKEN:
        logger.error("Не установлены TELEGRAM_TOKEN или HUGGINGFACE_API_KEY")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    from telegram.ext import CommandHandler
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
