import logging
from telegram import BotCommand, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import CUSTOMER_BOT_TOKEN, SERVER_URL
from database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton(
            text="📋 Меню",
            web_app=WebAppInfo(url=f"{SERVER_URL}"),
        )]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "☕ Добро пожаловать!\n\n"
        "Нажмите «Меню» чтобы открыть каталог.\n"
        "Выберите категорию, товар и объём — заказ уйдёт бариста.\n\n"
        "Статус заказа приходит сюда сообщением.",
        reply_markup=reply_markup,
    )


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Открыть меню кафе"),
    ])
    await application.bot.set_chat_menu_button(
        menu_button=KeyboardButton(text="☕ Меню", web_app=WebAppInfo(url=f"{SERVER_URL}"))
    )
    logger.info("Customer bot commands set")


def main():
    init_db()
    application = (
        Application.builder()
        .token(CUSTOMER_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    application.add_handler(CommandHandler("start", cmd_start))
    logger.info("Customer bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
