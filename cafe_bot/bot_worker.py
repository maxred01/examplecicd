import logging
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import WORKER_BOT_TOKEN
from database import init_db, get_order, update_order_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_order(order, header="📦 *Новый заказ*"):
    return (
        f"{header} *#{order['id']}*\n\n"
        f"👤 {order['username'] or 'Гость'}\n"
        f"☕ {order['product_name']}\n"
        f"📏 {order['variant_label']}\n"
        f"💰 {order['price']} ₽\n"
    )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧑‍🍳 Бот-работник кафе запущен.\n\n"
        "Сюда будут поступать заказы из мини-приложения.\n"
        "Вы сможете принять, выполнить или отклонить каждый заказ."
    )


async def handle_order_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, order_id_str = data.split("_", 1)
    order_id = int(order_id_str)

    order = get_order(order_id)
    if not order:
        await query.edit_message_text("⚠️ Заказ не найден.")
        return

    if action == "accept":
        if order["status"] != "pending":
            await query.edit_message_text(f"📦 Заказ #{order_id} уже обработан ({order['status']}).")
            return

        update_order_status(order_id, "accepted")

        new_text = (
            f"✅ Заказ *#{order_id}* принят\n\n"
            f"👤 {order['username'] or 'Гость'}\n"
            f"☕ {order['product_name']}\n"
            f"📏 {order['variant_label']}\n"
            f"💰 {order['price']} ₽\n"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏁 Выполнено", callback_data=f"complete_{order_id}")]
        ])
        await query.edit_message_text(text=new_text, reply_markup=keyboard, parse_mode="Markdown")

        try:
            await context.bot.send_message(
                chat_id=order["user_id"],
                text=f"✅ Заказ *#{order_id}* принят бариста!\n\n"
                     f"☕ {order['product_name']} ({order['variant_label']})\n"
                     f"Ожидайте, готовим ваш заказ.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Could not notify user {order['user_id']}: {e}")

    elif action == "decline":
        if order["status"] != "pending":
            await query.edit_message_text(f"📦 Заказ #{order_id} уже обработан ({order['status']}).")
            return

        update_order_status(order_id, "declined")

        new_text = (
            f"❌ Заказ *#{order_id}* отклонён\n\n"
            f"👤 {order['username'] or 'Гость'}\n"
            f"☕ {order['product_name']}\n"
            f"📏 {order['variant_label']}\n"
        )
        await query.edit_message_text(text=new_text, parse_mode="Markdown")

        try:
            await context.bot.send_message(
                chat_id=order["user_id"],
                text=f"❌ Заказ *#{order_id}* отменён.\n\n"
                     f"☕ {order['product_name']} ({order['variant_label']})\n"
                     f"К сожалению, заказ не может быть выполнен.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Could not notify user {order['user_id']}: {e}")

    elif action == "complete":
        if order["status"] != "accepted":
            await query.edit_message_text(f"📦 Заказ #{order_id} в статусе «{order['status']}».")
            return

        update_order_status(order_id, "completed")

        new_text = (
            f"🏁 Заказ *#{order_id}* выполнен!\n\n"
            f"👤 {order['username'] or 'Гость'}\n"
            f"☕ {order['product_name']}\n"
            f"📏 {order['variant_label']}\n"
        )
        await query.edit_message_text(text=new_text, parse_mode="Markdown")

        try:
            await context.bot.send_message(
                chat_id=order["user_id"],
                text=f"🏁 Заказ *#{order_id}* готов!\n\n"
                     f"☕ {order['product_name']} ({order['variant_label']})\n"
                     f"Можете забрать на стойке.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Could not notify user {order['user_id']}: {e}")


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Запуск бота-работника"),
    ])
    logger.info("Worker bot commands set")


def main():
    init_db()
    application = (
        Application.builder()
        .token(WORKER_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CallbackQueryHandler(handle_order_action))
    logger.info("Worker bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
