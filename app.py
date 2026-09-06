# app.py
from flask import Flask
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/health')
def health():
    return "OK", 200

# ----- КЛАВИАТУРЫ -----
def main_menu():
    keyboard = [
        [InlineKeyboardButton("Игровые", callback_data="games")],
        [InlineKeyboardButton("Telegram", callback_data="telegram")],
        [InlineKeyboardButton("Другие", callback_data="other")]
    ]
    return InlineKeyboardMarkup(keyboard)

def games_menu():
    keyboard = [
        [InlineKeyboardButton("Zagruzka.by", callback_data="zagruzka")],
        [InlineKeyboardButton("Game-Online.by", callback_data="gameonline")],
        [InlineKeyboardButton("Belconsole.by", callback_data="belconsole")],
        [InlineKeyboardButton("GGSel", callback_data="ggsel")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def telegram_menu():
    keyboard = [
        [InlineKeyboardButton("LaLYoU Stars Bot", callback_data="lalyou")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def other_menu():
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ----- ОБРАБОТЧИКИ -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте!\n\nВыберите категорию сервисов, которые вам нужны:",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "games":
        await query.edit_message_text(
            "Вы выбрали категорию \"Игровые\".\n\nВыберите сервис:",
            reply_markup=games_menu()
        )

    elif data == "telegram":
        await query.edit_message_text(
            "Вы выбрали категорию \"Telegram\".\n\nВыберите сервис:",
            reply_markup=telegram_menu()
        )

    elif data == "other":
        await query.edit_message_text(
            "Вы выбрали категорию \"Другие\".\n\nСписок сервисов скоро появится.",
            reply_markup=other_menu()
        )

    elif data == "zagruzka":
        await query.edit_message_text(
            "🎮 Zagruzka.by\n\n"
            "Сайт: https://zagruzka.by\n"
            "Описание: Цифровой маркетплейс лицензионных игр.",
            reply_markup=games_menu()
        )

    elif data == "gameonline":
        await query.edit_message_text(
            "🎮 Game-Online.by\n\n"
            "Сайт: https://game-online.by\n"
            "Описание: Интернет-магазин лицензионных ключей для PC и консолей.",
            reply_markup=games_menu()
        )

    elif data == "belconsole":
        await query.edit_message_text(
            "🎮 Belconsole.by\n\n"
            "Сайт: https://belconsole.by\n"
            "Описание: Площадка, где продаются цифровые коды активации, ключи для Steam и подписки для консолей.",
            reply_markup=games_menu()
        )

    elif data == "ggsel":
        await query.edit_message_text(
            "🎮 GGSel\n\n"
            "Сайт: https://ggsel.net\n"
            "Описание: Торговая площадка, где независимые продавцы предлагают ключи к играм, игровую валюту, аккаунты, подписки и программное обеспечение для различных платформ.",
            reply_markup=games_menu()
        )

    elif data == "lalyou":
        await query.edit_message_text(
            "🤖 LaLYoU Stars Bot\n\n"
            "Бот в Telegram: @LaLYoUStarsbot\n"
            "Описание: Бот для покупки звёзд, премиума, удалённых подарков, аренды NFT.",
            reply_markup=telegram_menu()
        )

    elif data == "back":
        await query.edit_message_text(
            "Здравствуйте!\n\nВыберите категорию сервисов, которые вам нужны:",
            reply_markup=main_menu()
        )

# ----- ЗАПУСК -----
def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    import threading
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False),
        daemon=True
    ).start()
    run_bot()
