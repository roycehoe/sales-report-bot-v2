from dotenv import dotenv_values
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    Application,
    MessageHandler,
    filters,
)

CONFIG = dotenv_values()

TOKEN = CONFIG.get("TOKEN", "") or ""
CHAT_ID = -4000147220

message_history = []


def store_message(update: Update, context: Application) -> None:
    if message := update.message:
        message_history.append(message)


async def show_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if message := update.message:
        await message.reply_text(f"{message_history}")


application = Application.builder().token(TOKEN).build()
message_handler = MessageHandler(filters.Chat(chat_id=CHAT_ID), store_message)
application.add_handler(message_handler)

application.add_handler(CommandHandler("show", show_messages))

application.run_polling(allowed_updates=Update.ALL_TYPES)
