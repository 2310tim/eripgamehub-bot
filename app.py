# app.py
from flask import Flask
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден")

ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
if not ADMIN_ID:
    raise ValueError("ADMIN_CHAT_ID не задан. Добавьте в переменные окружения.")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/health')
def health():
    return "OK", 200

# ----- ГЛАВНОЕ МЕНЮ (с динамической кнопкой для админа) -----
def main_menu(user_id):
    keyboard = [
        [InlineKeyboardButton("📂 Категории сервисов", callback_data="categories")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="tutorial")],
        [InlineKeyboardButton("📩 Связь", callback_data="contact")]
    ]

    # Если пользователь — админ, добавляем скрытую кнопку
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ Админ-панель", callback_data="admin_panel")])

    return InlineKeyboardMarkup(keyboard)

# ----- КЛАВИАТУРЫ КАТЕГОРИЙ -----
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

# ----- КНОПКИ ДЛЯ ВОЗВРАТА -----
def back_to_games_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад к списку сервисов", callback_data="back_to_games")]
    ])

def back_to_telegram_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад к списку сервисов", callback_data="back_to_telegram")]
    ])

def back_to_other_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад к списку сервисов", callback_data="back_to_other")]
    ])

# ----- ОБРАБОТЧИКИ -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        "👋 Здравствуйте!\n\nВыберите действие:",
        reply_markup=main_menu(user_id)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    # ---- ГЛАВНОЕ МЕНЮ ----
    if data == "categories":
        await query.edit_message_text(
            "📂 Выберите категорию сервисов:",
            reply_markup=categories_menu()
        )

    elif data == "tutorial":
        await query.edit_message_text(
            "📖 Инструкция по оплате через терминал Киви\n\n"
            "К сожалению, инструкция ещё в разработке.\n"
            "Она появится в ближайшее время.\n\n"
            "Следите за обновлениями!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
            ])
        )

    elif data == "contact":
        await query.edit_message_text(
            "📩 Вы выбрали 'Связь'.\n\nПожалуйста, напишите ваше сообщение. Я перешлю его администратору.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
            ])
        )
        context.user_data['awaiting_message'] = True

    # ---- АДМИН-ПАНЕЛЬ (только для админа) ----
    elif data == "admin_panel":
        if user_id != ADMIN_ID:
            await query.edit_message_text("⛔ У вас нет доступа к этой кнопке.")
            return

        await query.edit_message_text(
            "⚙️ Админ-панель\n\n"
            "Здесь будут доступны функции для управления ботом:\n"
            "• 📊 Статистика\n"
            "• 📨 Рассылка\n"
            "• 🛠 Управление сервисами\n\n"
            "Пока что это заглушка. Функционал появится позже.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
            ])
        )

    # ---- НАЗАД В ГЛАВНОЕ МЕНЮ ----
    elif data == "back_main":
        await query.edit_message_text(
            "👋 Здравствуйте!\n\nВыберите действие:",
            reply_markup=main_menu(user_id)
        )

    elif data == "back_categories":
        await query.edit_message_text(
            "📂 Выберите категорию сервисов:",
            reply_markup=categories_menu()
        )

    elif data == "back_to_games":
        await query.delete_message()
        await query.message.reply_text(
            "🎮 Вы выбрали категорию 'Игровые'.\n\nВыберите сервис:",
            reply_markup=games_menu()
        )

    elif data == "back_to_telegram":
        await query.delete_message()
        await query.message.reply_text(
            "📱 Вы выбрали категорию 'Telegram'.\n\nВыберите сервис:",
            reply_markup=telegram_menu()
        )

    elif data == "back_to_other":
        await query.delete_message()
        await query.message.reply_text(
            "📦 Вы выбрали категорию 'Другие'.\n\nСписок сервисов скоро появится.",
            reply_markup=other_menu()
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

    # ----- СЕРВИСЫ -----
    elif data == "belconsole":
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/7",
            caption="🎮 Belconsole.by\n\nСайт: https://belconsole.by\nОписание: Площадка, где продаются цифровые коды активации, ключи для Steam и подписки для консолей.",
            reply_markup=back_to_games_menu()
        )
        await query.delete_message()

    elif data == "donatov":
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/5",
            caption="🎮 Donatov.Net\n\nСайт: https://donatov.net\nОписание: Платформа для донатов, пополнения игровых аккаунтов и покупки внутриигровой валюты.",
            reply_markup=back_to_games_menu()
        )
        await query.delete_message()

    elif data == "gameonline":
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/4",
            caption="🎮 Game-Online.by\n\nСайт: https://game-online.by\nОписание: Интернет-магазин лицензионных ключей для PC и консолей.",
            reply_markup=back_to_games_menu()
        )
        await query.delete_message()

    elif data == "ggsel":
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/8",
            caption="🎮 GGSel\n\nСайт: https://ggsel.net\nОписание: Торговая площадка, где независимые продавцы предлагают ключи к играм, игровую валюту, аккаунты, подписки и программное обеспечение для различных платформ.",
            reply_markup=back_to_games_menu()
        )
        await query.delete_message()

    elif data == "zagruzka":
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/6",
            caption="🎮 Zagruzka.by\n\nСайт: https://zagruzka.by\nОписание: Цифровой маркетплейс лицензионных игр.",
            reply_markup=back_to_games_menu()
        )
        await query.delete_message()

    elif data == "lalyou":
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/2",
            caption="🤖 LaLYoU Stars Bot\n\nБот в Telegram: @LaLYoUStarsbot\nОписание: Бот для покупки звёзд, премиума, удалённых подарков, аренды NFT.",
            reply_markup=back_to_telegram_menu()
        )
        await query.delete_message()

# ----- ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ (для Связи) -----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.user_data.get('awaiting_message'):
        user = update.effective_user
        text = update.message.text

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 Новое сообщение от пользователя:\n\n"
                 f"👤 Имя: {user.first_name}\n"
                 f"🆔 ID: {user.id}\n"
                 f"📝 Сообщение:\n{text}"
        )

        await update.message.reply_text(
            "✅ Ваше сообщение отправлено администратору!\n\nОжидайте ответа. Спасибо!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 В главное меню", callback_data="back_main")]
            ])
        )
        context.user_data['awaiting_message'] = False
    else:
        await update.message.reply_text(
            "Используйте кнопку 'Связь' в меню, чтобы отправить сообщение администратору.",
            reply_markup=main_menu(user_id)
        )

# ----- ЗАПУСК -----
def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    import threading
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False),
        daemon=True
    ).start()
    run_bot()
