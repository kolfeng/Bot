import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from flask import Flask
from threading import Thread
import time

# ================== FLASK ДЛЯ RENDER ==================
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <body>
            <h1>🤖 Telegram AI Bot is Running!</h1>
            <p>Бот активен и готов к работе!</p>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "ok", "bot": "running"}

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# ================== TELEGRAM BOT ==================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
                    "max_new_tokens": 100,
                    "temperature": 0.8,
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
                return f"❌ Ошибка API (код: {response.status_code})"
                
        except Exception as e:
            return f"⚠️ Ошибка соединения: {str(e)}"

ai_bot = AIChatBot(HUGGINGFACE_TOKEN)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🤖 **Привет! Я AI-бот**

Используется нейросеть Microsoft DialoGPT-medium

Просто напиши мне сообщение, и я отвечу!
    """
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "💡 Просто напиши любое сообщение - я постараюсь ответить!"
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Сообщение от пользователя: {user_message}")
    
    await update.message.chat.send_action(action="typing")
    
    bot_response = ai_bot.get_ai_response(user_message)
    
    await update.message.reply_text(bot_response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка в боте: {context.error}")

def run_telegram_bot():
    """Запуск Telegram бота"""
    if not TELEGRAM_TOKEN:
        logger.error("❌ Не установлен TELEGRAM_TOKEN")
        return
    if not HUGGINGFACE_TOKEN:
        logger.error("❌ Не установлен HUGGINGFACE_API_KEY")
        return
    
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        application.add_error_handler(error_handler)
        
        logger.info("🚀 Бот запускается...")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")

if __name__ == "__main__":
    logger.info("🎯 Starting application...")
    
    # Запускаем Flask сервер в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    logger.info("🌐 Flask server started on port 5000")
    
    # Даем Flask время запуститься
    time.sleep(2)
    
    # Запускаем Telegram бота
    run_telegram_bot()
