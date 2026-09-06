from flask import Flask
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

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

# ---- КНОПКИ ----
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Игровые", callback_data="category_games")],
        [InlineKeyboardButton("Другие", callback_data="category_other")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте!\n\nВыберите категорию сервисов:",
        reply_markup=main_menu_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "category_games":
        text = "Вы выбрали категорию \"Игровые\".\n\nВыберите сервис:"
        keyboard = [
            [InlineKeyboardButton("Donatov.Net", callback_data="service_donatov")],
            [InlineKeyboardButton("GGSel", callback_data="service_ggsel")],
            [InlineKeyboardButton("Назад", callback_data="back_to_main")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "service_donatov":
        await query.edit_message_text("Donatov.Net\nСайт: https://donatov.net", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад", callback_data="category_games")]
        ]))
    
    elif data == "back_to_main":
        await query.edit_message_text("Главное меню", reply_markup=main_menu_keyboard())

def main():
    app_bot = Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущен!")
    app_bot.run_polling()

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False), daemon=True).start()
    main()
