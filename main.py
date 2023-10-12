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


async def show_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if message := update.message:
        await message.reply_text(f"{message_history}")


application = Application.builder().token(TOKEN).build()
message_store = MessageStore()

# message_handler = MessageHandler(filters.Chat(chat_id=CHAT_ID), store_message)
message_handler = MessageHandler(filters.Chat(chat_id=CHAT_ID), message_store.store)
application.add_handler(message_handler)

# application.add_handler(CommandHandler("show", show_messages))
message_history = message_store.messages
application.add_handler(CommandHandler("show", show_messages))

application.run_polling(allowed_updates=Update.ALL_TYPES)
