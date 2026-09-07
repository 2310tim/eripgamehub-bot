# app.py
from flask import Flask
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден")

ADMIN_ID = os.getenv("ADMIN_CHAT_ID")
if not ADMIN_ID:
    raise ValueError("ADMIN_CHAT_ID не задан. Добавьте в переменные окружения.")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/health')
def health():
    return "OK", 200

# ----- ГЛАВНОЕ МЕНЮ -----
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📂 Категории сервисов", callback_data="categories")],
        [InlineKeyboardButton("📩 Связь", callback_data="contact")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ----- КЛАВИАТУРЫ КАТЕГОРИЙ (в алфавитном порядке) -----
def categories_menu():
    keyboard = [
        [InlineKeyboardButton("Игровые", callback_data="games")],
        [InlineKeyboardButton("Telegram", callback_data="telegram")],
        [InlineKeyboardButton("Другие", callback_data="other")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def games_menu():
    keyboard = [
        [InlineKeyboardButton("Belconsole.by", callback_data="belconsole")],
        [InlineKeyboardButton("Donatov.Net", callback_data="donatov")],
        [InlineKeyboardButton("Game-Online.by", callback_data="gameonline")],
        [InlineKeyboardButton("GGSel", callback_data="ggsel")],
        [InlineKeyboardButton("Zagruzka.by", callback_data="zagruzka")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_categories")]
    ]
    return InlineKeyboardMarkup(keyboard)

def telegram_menu():
    keyboard = [
        [InlineKeyboardButton("LaLYoU Stars Bot", callback_data="lalyou")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_categories")]
    ]
    return InlineKeyboardMarkup(keyboard)

def other_menu():
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_categories")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ----- ОБРАБОТЧИКИ -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Здравствуйте!\n\n"
        "Выберите действие:",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ---- ГЛАВНОЕ МЕНЮ ----
    if data == "categories":
        await query.edit_message_text(
            "📂 Выберите категорию сервисов:",
            reply_markup=categories_menu()
        )

    elif data == "contact":
        await query.edit_message_text(
            "📩 Вы выбрали 'Связь'.\n\n"
            "Пожалуйста, напишите ваше сообщение. "
            "Я перешлю его администратору.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
            ])
        )
        # Устанавливаем состояние, что пользователь в режиме отправки сообщения
        context.user_data['awaiting_message'] = True

    # ---- НАЗАД ----
    elif data == "back_main":
        await query.edit_message_text(
            "👋 Здравствуйте!\n\nВыберите действие:",
            reply_markup=main_menu()
        )

    elif data == "back_categories":
        await query.edit_message_text(
            "📂 Выберите категорию сервисов:",
            reply_markup=categories_menu()
        )

    # ---- КАТЕГОРИИ ----
    elif data == "games":
        await query.edit_message_text(
            "🎮 Вы выбрали категорию 'Игровые'.\n\nВыберите сервис:",
            reply_markup=games_menu()
        )

    elif data == "telegram":
        await query.edit_message_text(
            "📱 Вы выбрали категорию 'Telegram'.\n\nВыберите сервис:",
            reply_markup=telegram_menu()
        )

    elif data == "other":
        await query.edit_message_text(
            "📦 Вы выбрали категорию 'Другие'.\n\nСписок сервисов скоро появится.",
            reply_markup=other_menu()
        )

    # ---- СЕРВИСЫ ----
    elif data == "belconsole":
        await query.edit_message_text(
            "🎮 Belconsole.by\n\n"
            "Сайт: https://belconsole.by\n"
            "Описание: Площадка, где продаются цифровые коды активации, ключи для Steam и подписки для консолей.",
            reply_markup=games_menu()
        )

    elif data == "donatov":
        await query.edit_message_text(
            "🎮 Donatov.Net\n\n"
            "Сайт: https://donatov.net\n"
            "Описание: Платформа для донатов, пополнения игровых аккаунтов и покупки внутриигровой валюты.",
            reply_markup=games_menu()
        )

    elif data == "gameonline":
        await query.edit_message_text(
            "🎮 Game-Online.by\n\n"
            "Сайт: https://game-online.by\n"
            "Описание: Интернет-магазин лицензионных ключей для PC и консолей.",
            reply_markup=games_menu()
        )

    elif data == "ggsel":
        await query.edit_message_text(
            "🎮 GGSel\n\n"
            "Сайт: https://ggsel.net\n"
            "Описание: Торговая площадка, где независимые продавцы предлагают ключи к играм, игровую валюту, аккаунты, подписки и программное обеспечение для различных платформ.",
            reply_markup=games_menu()
        )

    elif data == "zagruzka":
        await query.edit_message_text(
            "🎮 Zagruzka.by\n\n"
            "Сайт: https://zagruzka.by\n"
            "Описание: Цифровой маркетплейс лицензионных игр.",
            reply_markup=games_menu()
        )

    elif data == "lalyou":
        await query.edit_message_text(
            "🤖 LaLYoU Stars Bot\n\n"
            "Бот в Telegram: @LaLYoUStarsbot\n"
            "Описание: Бот для покупки звёзд, премиума, удалённых подарков, аренды NFT.",
            reply_markup=telegram_menu()
        )

# ----- ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ (для Связи) -----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, находится ли пользователь в режиме отправки сообщения
    if context.user_data.get('awaiting_message'):
        user = update.effective_user
        text = update.message.text
        
        # Отправляем сообщение админу
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 Новое сообщение от пользователя:\n\n"
                 f"👤 Имя: {user.first_name}\n"
                 f"🆔 ID: {user.id}\n"
                 f"📝 Сообщение:\n{text}"
        )
        
        # Подтверждаем пользователю
        await update.message.reply_text(
            "✅ Ваше сообщение отправлено администратору!\n\n"
            "Ожидайте ответа. Спасибо!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 В главное меню", callback_data="back_main")]
            ])
        )
        
        # Сбрасываем состояние
        context.user_data['awaiting_message'] = False
    else:
        # Если пользователь просто пишет боту, а не через кнопку "Связь"
        await update.message.reply_text(
            "Используйте кнопку 'Связь' в меню, чтобы отправить сообщение администратору.",
            reply_markup=main_menu()
        )

# ----- ЗАПУСК -----
def run_bot():
    application = Application.builder().token(TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    
    # Кнопки
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Текстовые сообщения (для Связи)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    import threading
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False),
        daemon=True
    ).start()
    run_bot()
