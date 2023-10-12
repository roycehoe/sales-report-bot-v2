from dataclasses import dataclass
from datetime import datetime
from dotenv import dotenv_values
import pytz
from telegram import Message, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    Application,
    MessageHandler,
    filters,
)

from display import get_display

CONFIG = dotenv_values()
TOKEN = CONFIG.get("TOKEN", "") or ""
CHAT_ID = CONFIG.get("CHAT_ID", "") or ""


class MessageStore:
    messages: list[Message] = []

    def store(self, update: Update, context: Application) -> None:
        if message := update.message:
            self.messages.append(message)


class MessageFormatter:
    def __init__(self, message_store: MessageStore):
        self.message_store = message_store

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if message := update.message:
            display = get_display(self.message_store.messages)
            await message.reply_text(f"{display}")

    async def show_with_date_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            date = datetime.strptime(update.message.text, "%d-%m-%Y")
        except Exception:
            await update.message.reply_text("Invalid date. Please try again")
            return

        if message := update.message:
            display = get_display(message_store.messages, date)
            await message.reply_text(f"{display}")


application = Application.builder().token(TOKEN).build()
message_store = MessageStore()
message_formatter = MessageFormatter(message_store)

message_handler = MessageHandler(filters.Chat(chat_id=CHAT_ID), message_store.store)
application.add_handler(message_handler)
application.add_handler(CommandHandler("show", message_formatter.show))
application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND, message_formatter.show_with_date_input
    )
)
application.run_polling(allowed_updates=Update.ALL_TYPES)
