# app.py
# Telegram anonymous complaints bot (aiogram v3) + Flask (Render friendly)
from flask import Flask
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ---- ТОКЕН ИЗ ПЕРЕМЕННОЙ ОКРУЖЕНИЯ ----
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден. Пожалуйста, добавьте TELEGRAM_TOKEN в переменные окружения.")

# ---- FLASK ДЛЯ RENDER ----
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает."

@app.route('/health')
def health():
    return "OK", 200

# ---- КНОПКИ ГЛАВНОГО МЕНЮ ----
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Игровые", callback_data="category_games")],
        [InlineKeyboardButton("Другие", callback_data="category_other")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ---- КНОПКИ ДЛЯ КАТЕГОРИИ "ИГРОВЫЕ" ----
def games_keyboard():
    keyboard = [
        [InlineKeyboardButton("Donatov.Net", callback_data="service_donatov")],
        [InlineKeyboardButton("GGSel", callback_data="service_ggsel")],
        [InlineKeyboardButton("Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ---- КНОПКИ ДЛЯ КАТЕГОРИИ "ДРУГИЕ" (ПОКА ЗАГЛУШКА) ----
def other_keyboard():
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ---- КОМАНДА /START ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Здравствуйте!\n\n"
        "Выберите категорию сервисов, которые вам нужны:"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())

# ---- ОБРАБОТЧИК КНОПОК ----
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # ---- КАТЕГОРИЯ "ИГРОВЫЕ" ----
    if data == "category_games":
        text = "Вы выбрали категорию \"Игровые\".\n\nВыберите сервис:"
        await query.edit_message_text(text, reply_markup=games_keyboard())

    # ---- КАТЕГОРИЯ "ДРУГИЕ" ----
    elif data == "category_other":
        text = "Вы выбрали категорию \"Другие\".\n\nСписок сервисов скоро появится."
        await query.edit_message_text(text, reply_markup=other_keyboard())

    # ---- СЕРВИС: DONATOV.NET ----
    elif data == "service_donatov":
        text = (
            "Donatov.Net\n\n"
            "Сайт: https://donatov.net\n"
            "Данный раздел находится в разработке."
        )
        await query.edit_message_text(text, reply_markup=games_keyboard())

    # ---- СЕРВИС: GGSEL ----
    elif data == "service_ggsel":
        text = (
            "GGSel\n\n"
            "Сайт: https://ggsel.net\n"
            "Данный раздел находится в разработке."
        )
        await query.edit_message_text(text, reply_markup=games_keyboard())

    # ---- НАЗАД В ГЛАВНОЕ МЕНЮ ----
    elif data == "back_to_main":
        text = "Здравствуйте!\n\nВыберите категорию сервисов, которые вам нужны:"
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())

# ---- ЗАПУСК БОТА ----
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Бот успешно запущен.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    main()
