import datetime
from dotenv import dotenv_values
from telegram import Message, Update
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


class MessageStore:
    messages: list[Message] = []

    def store(self, update: Update, context: Application) -> None:
        if message := update.message:
            self.messages.append(message)

    def filter_by_date(
        self,
        date: datetime.datetime = datetime.datetime.today(),
    ):
        return [
            message for message in self.messages if message.date.date() == date.date()
        ]


class MessageFormatter:
    def __init__(self, message_store: MessageStore):
        self.message_store = message_store

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if message := update.message:
            await message.reply_text(f"{message_store.messages}")


application = Application.builder().token(TOKEN).build()
message_store = MessageStore()
message_formatter = MessageFormatter(message_store)

message_handler = MessageHandler(filters.Chat(chat_id=CHAT_ID), message_store.store)
application.add_handler(message_handler)
application.add_handler(CommandHandler("show", message_formatter.show))

application.run_polling(allowed_updates=Update.ALL_TYPES)
