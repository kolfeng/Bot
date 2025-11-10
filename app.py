import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

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
        try:
            payload = {
                "inputs": message,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.9,
                    "do_sample": True,
                }
            }
            
            response = requests.post(
                self.model_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', 'Не удалось сгенерировать ответ')
                return "Получен пустой ответ"
                
            elif response.status_code == 503:
                return "🔄 Модель загружается... Подождите 20-30 секунд."
            else:
                return "❌ Ошибка API. Попробуйте позже."
                
        except Exception as e:
            return f"⚠️ Ошибка: {str(e)}"

ai_bot = AIChatBot(HUGGINGFACE_TOKEN)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "🤖 Привет! Я AI-бот. Напиши мне сообщение!"
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")
    bot_response = ai_bot.get_ai_response(user_message)
    await update.message.reply_text(bot_response)

def main():
    if not TELEGRAM_TOKEN:
        logger.error("Не установлен TELEGRAM_TOKEN")
        return
    if not HUGGINGFACE_TOKEN:
        logger.error("Не установлен HUGGINGFACE_API_KEY")
        return
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
