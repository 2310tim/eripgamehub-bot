# app.py
from flask import Flask
import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден")

ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
if not ADMIN_ID:
    raise ValueError("ADMIN_CHAT_ID не задан. Добавьте в переменные окружения.")

app = Flask(__name__)

# ===== ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ =====
conn = sqlite3.connect("stats.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stats (
        key TEXT PRIMARY KEY,
        value INTEGER DEFAULT 0
    )
""")
conn.commit()

def increment_stat(key):
    cursor.execute(
        "INSERT INTO stats (key, value) VALUES (?, 1) ON CONFLICT(key) DO UPDATE SET value = value + 1",
        (key,)
    )
    conn.commit()

def get_stat(key):
    cursor.execute("SELECT value FROM stats WHERE key = ?", (key,))
    result = cursor.fetchone()
    return result[0] if result else 0

def get_all_stats():
    cursor.execute("SELECT key, value FROM stats")
    return dict(cursor.fetchall())

# ===== КЛАВИАТУРЫ =====
def main_menu(user_id):
    keyboard = [
        [InlineKeyboardButton("📂 Категории сервисов", callback_data="categories")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="tutorial")],
        [InlineKeyboardButton("📩 Связь", callback_data="contact")]
    ]
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ Админ-панель", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)

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

# ----- КНОПКА "ИНСТРУКЦИЯ" ДЛЯ GGSEL -----
def ggsel_with_instruction():
    keyboard = [
        [InlineKeyboardButton("📖 Инструкция (Обязательно к прочтению)", callback_data="ggsel_instruction")],
        [InlineKeyboardButton("🔙 Назад к списку сервисов", callback_data="back_to_games")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== ИНСТРУКЦИЯ (ОБЩАЯ) =====
def tutorial_keyboard(step):
    keyboard = []
    if step > 1:
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data=f"tutorial_back_{step}")])
    if step < 2:
        keyboard.append([InlineKeyboardButton("Вперед ▶️", callback_data=f"tutorial_forward_{step}")])
    keyboard.append([InlineKeyboardButton("🏠 В главное меню", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

# ===== ОБРАБОТЧИКИ =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    increment_stat("total_users")
    increment_stat("total_messages")
    await update.message.reply_text(
        "👋 Здравствуйте!\n\nВыберите действие:",
        reply_markup=main_menu(user_id)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    increment_stat("total_messages")

    # ---- ГЛАВНОЕ МЕНЮ ----
    if data == "categories":
        await query.edit_message_text(
            "📂 Выберите категорию сервисов:",
            reply_markup=categories_menu()
        )

    elif data == "tutorial":
        text = (
            "📖 **Инструкция по оплате через терминал QIWI**\n\n"
            "**Шаг 1 из 2**\n\n"
            "Подойдите к терминалу QIWI. Нажмите на кнопку **ЕРИП**, "
            "на которую указана стрелка на картинке.\n\n"
            "Инструкция будет дополнена позже."
        )
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=tutorial_keyboard(1)
        )

    elif data == "contact":
        increment_stat("contact")
        await query.edit_message_text(
            "📩 Вы выбрали 'Связь'.\n\nПожалуйста, напишите ваше сообщение. Я перешлю его администратору.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
            ])
        )
        context.user_data['awaiting_message'] = True

    # ---- ИНСТРУКЦИЯ GGSEL ----
    elif data == "ggsel_instruction":
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/10",
            caption=(
                "📖 **Инструкция по оплате через GGSel**\n\n"
                "Нажмите на кнопку **\"Да\"**, которая указана на картинке, чтобы продолжить."
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Вернуться", callback_data="ggsel_back")]
            ])
        )
        await query.delete_message()

    elif data == "ggsel_back":
        # Возврат к карточке GGSel
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/8",
            caption="🎮 GGSel\n\nСайт: https://ggsel.net\nОписание: Торговая площадка, где независимые продавцы предлагают ключи к играм, игровую валюту, аккаунты, подписки и программное обеспечение для различных платформ.",
            reply_markup=ggsel_with_instruction()
        )
        await query.delete_message()

    # ---- ИНСТРУКЦИЯ: НАВИГАЦИЯ ----
    elif data.startswith("tutorial_forward_"):
        current_step = int(data.split("_")[2])
        next_step = current_step + 1
        
        if next_step <= 2:
            if next_step == 2:
                text = (
                    "📖 **Инструкция по оплате через терминал QIWI**\n\n"
                    "**Шаг 2 из 2**\n\n"
                    "Инструкция будет добавлена позже. Следите за обновлениями!"
                )
            else:
                text = f"📖 **Шаг {next_step}**\n\nИнструкция будет добавлена позже."
            
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=tutorial_keyboard(next_step)
            )

    elif data.startswith("tutorial_back_"):
        current_step = int(data.split("_")[2])
        prev_step = current_step - 1
        
        if prev_step == 1:
            text = (
                "📖 **Инструкция по оплате через терминал QIWI**\n\n"
                "**Шаг 1 из 2**\n\n"
                "Подойдите к терминалу QIWI. Нажмите на кнопку **ЕРИП**, "
                "на которую указана стрелка на картинке.\n\n"
                "Инструкция будет дополнена позже."
            )
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=tutorial_keyboard(prev_step)
            )

    # ---- АДМИН-ПАНЕЛЬ ----
    elif data == "admin_panel":
        if user_id != ADMIN_ID:
            await query.edit_message_text("⛔ У вас нет доступа.")
            return

        text = (
            f"📊 **Статистика бота**\n\n"
            f"👤 **Всего пользователей:** {get_stat('total_users')}\n"
            f"📩 **Обращений через «Связь»:** {get_stat('contact')}\n"
            f"🔄 **Всего действий:** {get_stat('total_messages')}\n\n"
            f"📂 **Популярность категорий:**\n"
            f"  🎮 Игровые: {get_stat('category_games')}\n"
            f"  📱 Telegram: {get_stat('category_telegram')}\n"
            f"  📦 Другие: {get_stat('category_other')}\n\n"
            f"🔥 **Популярность сервисов:**\n"
            f"  Belconsole.by: {get_stat('service_belconsole')}\n"
            f"  Donatov.Net: {get_stat('service_donatov')}\n"
            f"  Game-Online.by: {get_stat('service_gameonline')}\n"
            f"  GGSel: {get_stat('service_ggsel')}\n"
            f"  Zagruzka.by: {get_stat('service_zagruzka')}\n"
            f"  LaLYoU Stars Bot: {get_stat('service_lalyou')}"
        )

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="back_main")]
            ])
        )

    # ---- НАЗАД ----
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
        increment_stat("category_games")
        await query.edit_message_text(
            "🎮 Вы выбрали категорию 'Игровые'.\n\nВыберите сервис:",
            reply_markup=games_menu()
        )

    elif data == "telegram":
        increment_stat("category_telegram")
        await query.edit_message_text(
            "📱 Вы выбрали категорию 'Telegram'.\n\nВыберите сервис:",
            reply_markup=telegram_menu()
        )

    elif data == "other":
        increment_stat("category_other")
        await query.edit_message_text(
            "📦 Вы выбрали категорию 'Другие'.\n\nСписок сервисов скоро появится.",
            reply_markup=other_menu()
        )

    # ----- СЕРВИСЫ -----
    elif data == "belconsole":
        increment_stat("service_belconsole")
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/7",
            caption="🎮 Belconsole.by\n\nСайт: https://belconsole.by\nОписание: Площадка, где продаются цифровые коды активации, ключи для Steam и подписки для консолей.",
            reply_markup=back_to_games_menu()
        )
        await query.delete_message()

    elif data == "donatov":
        increment_stat("service_donatov")
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/5",
            caption="🎮 Donatov.Net\n\nСайт: https://donatov.net\nОписание: Платформа для донатов, пополнения игровых аккаунтов и покупки внутриигровой валюты.",
            reply_markup=back_to_games_menu()
        )
        await query.delete_message()

    elif data == "gameonline":
        increment_stat("service_gameonline")
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/4",
            caption="🎮 Game-Online.by\n\nСайт: https://game-online.by\nОписание: Интернет-магазин лицензионных ключей для PC и консолей.",
            reply_markup=back_to_games_menu()
        )
        await query.delete_message()

    elif data == "ggsel":
        increment_stat("service_ggsel")
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/8",
            caption="🎮 GGSel\n\nСайт: https://ggsel.net\nОписание: Торговая площадка, где независимые продавцы предлагают ключи к играм, игровую валюту, аккаунты, подписки и программное обеспечение для различных платформ.",
            reply_markup=ggsel_with_instruction()
        )
        await query.delete_message()

    elif data == "zagruzka":
        increment_stat("service_zagruzka")
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/6",
            caption="🎮 Zagruzka.by\n\nСайт: https://zagruzka.by\nОписание: Цифровой маркетплейс лицензионных игр.",
            reply_markup=back_to_games_menu()
        )
        await query.delete_message()

    elif data == "lalyou":
        increment_stat("service_lalyou")
        await query.message.reply_photo(
            photo="https://t.me/materialsERIPGameHub/2",
            caption="🤖 LaLYoU Stars Bot\n\nБот в Telegram: @LaLYoUStarsbot\nОписание: Бот для покупки звёзд, премиума, удалённых подарков, аренды NFT.",
            reply_markup=back_to_telegram_menu()
        )
        await query.delete_message()

# ----- ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ -----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    increment_stat("total_messages")

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
