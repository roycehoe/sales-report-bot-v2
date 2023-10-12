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


message_history = {}


def store_message(update: Update, context: Application) -> None:
    message = update.message
    chat_id = message.chat_id
    if chat_id not in message_history:
        message_history[chat_id] = []
    message_history[chat_id].append(message)

    # You can add additional logic here, like storing in a database


# async def show_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if not update.message:
#         return
#     await update.message.reply_text(f"Hello {update.effective_user.first_name}")


async def show_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(f"{message_history}")


def main() -> None:
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()

    # Add a MessageHandler to listen for all messages in group chats
    message_handler = MessageHandler(filters.Chat(chat_id=CHAT_ID), store_message)
    application.add_handler(message_handler)
    application.add_handler(CommandHandler("show", show_messages))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


# app = ApplicationBuilder().token(TOKEN).build()


# app.run_polling()

application = Application.builder().token(TOKEN).build()

# Add a MessageHandler to listen for all messages in group chats
message_handler = MessageHandler(filters.Chat(chat_id=CHAT_ID), store_message)
application.add_handler(message_handler)
application.add_handler(CommandHandler("show", show_messages))

# Run the bot until the user presses Ctrl-C
application.run_polling(allowed_updates=Update.ALL_TYPES)
