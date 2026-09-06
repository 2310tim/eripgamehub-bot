# app.py
from flask import Flask
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- Настройка ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден. Установите TELEGRAM_TOKEN в переменные окружения.")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/health')
def health():
    return "OK", 200

# --- Клавиатуры ---
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Игровые", callback_data="games")],
        [InlineKeyboardButton("Другие", callback_data="other")]
    ]
    return InlineKeyboardMarkup(keyboard)

def games_keyboard():
    keyboard = [
        [InlineKeyboardButton("Donatov.Net", callback_data="donatov")],
        [InlineKeyboardButton("GGSel", callback_data="ggsel")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def other_keyboard():
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Обработчики ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте!\n\nВыберите категорию сервисов:",
        reply_markup=main_menu_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "games":
        await query.edit_message_text(
            "Вы выбрали категорию \"Игровые\".\n\nВыберите сервис:",
            reply_markup=games_keyboard()
        )
    elif data == "other":
        await query.edit_message_text(
            "Вы выбрали категорию \"Другие\".\n\nСписок сервисов скоро появится.",
            reply_markup=other_keyboard()
        )
    elif data == "donatov":
        await query.edit_message_text(
            "Donatov.Net\nСайт: https://donatov.net",
            reply_markup=games_keyboard()
        )
    elif data == "ggsel":
        await query.edit_message_text(
            "GGSel\nСайт: https://ggsel.net",
            reply_markup=games_keyboard()
        )
    elif data == "back":
        await query.edit_message_text(
            "Здравствуйте!\n\nВыберите категорию сервисов:",
            reply_markup=main_menu_keyboard()
        )

# --- Запуск ---
def run_bot():
    # Создаём приложение
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем поллинг
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    import threading
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False),
        daemon=True
    ).start()
    
    # Запускаем бота
    run_bot()
