import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# Токен бота
TOKEN = "7859058780:AAHvBh7w7iNvc8KLE9Eq0RMfmjdwKYuAFOA"

# Стани
ASK_NAME, ASK_EMAIL, ASK_PHONE, ASK_OS = range(4)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    print(f"👉 Користувач натиснув /start: {user.id}")

    await update.message.reply_photo(photo=open("/Users/ruslanshevchenko/Desktop/rozgolos_start.jpg", "rb"))

    await update.message.reply_text(
        "Вас вітає офіційний бот юридичного застосунку ROZGOLOS 🇺🇦\n\n"
        "Ми допомагаємо при врученнях повісток, зупинках на блокпостах і в ситуаціях, коли система проти тебе.\n\n"
        "⚠️ Доступ до захисту можливий тільки після короткої анкети.\n❗️Недійсні заявки відхиляються.\n\n"
        "👤 Введіть ваше ІМ’Я ТА ПРІЗВИЩЕ (великими літерами):"
    )
    return ASK_NAME

# ПІБ
async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("**📧 Введіть EMAIL:**", parse_mode="Markdown")
    return ASK_EMAIL

# Email
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text.strip()
    await update.message.reply_text("**📞 Введіть НОМЕР ТЕЛЕФОНУ у форматі +380...**", parse_mode="Markdown")
    return ASK_PHONE

# Телефон
async def ask_os(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text.strip()
    keyboard = [["iOS"], ["Android"]]
    await update.message.reply_text(
        "**📲 Оберіть операційну систему вашого телефону:**",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return ASK_OS

# Завершення
async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    os_choice = update.message.text.strip()
    context.user_data['os'] = os_choice

    data = context.user_data
    user_info = (
        f"🆕 НОВА ЗАЯВКА\n\n"
        f"👤 ПІБ: **{data['name'].upper()}**\n"
        f"📧 EMAIL: **{data['email'].upper()}**\n"
        f"📞 ТЕЛЕФОН: **{data['phone'].upper()}**\n"
        f"📲 ОС: **{data['os'].upper()}**"
    )

    await context.bot.send_message(chat_id=7666787687, text=user_info, parse_mode="Markdown")

    if os_choice == "iOS":
        link = "https://apps.apple.com/app/id6739999117"
    else:
        link = "https://play.google.com/store/apps/details?id=com.rozgolos"

    keyboard = [[InlineKeyboardButton("🔒 ВСТАНОВИТИ ROZGOLOS", url=link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "✅ Дякуємо! Анкету прийнято.\n\n"
        "Натисніть кнопку нижче, щоб встановити застосунок та активувати захист 👇",
        reply_markup=reply_markup
    )

    return ConversationHandler.END
# Обробка помилок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="❌ ПОМИЛКА:", exc_info=context.error)

# Запуск
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_os)],
            ASK_OS: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish)]
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    print("✅ Бот запущено. Очікує на /start...")
    application.run_polling()
