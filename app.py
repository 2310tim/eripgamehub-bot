# app.py
from flask import Flask
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Токен
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден. Проверьте переменные окружения.")

# Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/health')
def health():
    return "OK", 200

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает! 🚀")

# Запуск бота
def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# Точка входа
if __name__ == "__main__":
    import threading
    
    # Запускаем Flask в отдельном потоке
    threading.Thread(
        target=lambda: app.run(
            host="0.0.0.0", 
            port=int(os.environ.get("PORT", 5000)),
            debug=False,
            use_reloader=False
        ),
        daemon=True
    ).start()
    
    # Запускаем бота
    run_bot()
