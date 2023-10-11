from dotenv import dotenv_values
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

CONFIG = dotenv_values()

TOKEN = CONFIG.get("TOKEN", "") or ""


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(f"Hello {update.effective_user.first_name}")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("hello", hello))

app.run_polling()
