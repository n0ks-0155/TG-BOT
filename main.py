import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import redis

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host='127.0.0.1',
    port=6379,
    db=0,
    decode_responses=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот, который сохраняет твои сообщения в Redis. Просто напиши что-нибудь.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text

    redis_key = f"user:{user_id}:messages"
    redis_client.rpush(redis_key, message_text)

    messages_count = redis_client.llen(redis_key)

    await update.message.reply_text(
        f"Ваше сообщение сохранено в Redis! Всего сообщений от вас: {messages_count}"
    )


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    redis_key = f"user:{user_id}:messages"

    messages_count = redis_client.llen(redis_key)
    last_messages = redis_client.lrange(redis_key, -5, -1)

    response = (
            f"Ваша статистика:\n"
            f"Всего сообщений: {messages_count}\n"
            f"Последние сообщения:\n- " + "\n- ".join(last_messages)
    )

    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    application = Application.builder().token("7923932560:AAF8vjcgwL7_tHJKtjJ92WDhuqoVIE7vmWo").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mystats", show_stats))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_error_handler(error)

    application.run_polling()


if __name__ == '__main__':
    main()

