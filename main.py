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

CONFIG = dotenv_values()

TOKEN = CONFIG.get("TOKEN", "") or ""
CHAT_ID = -4000147220
CURRENT_TIMEZONE = "Asia/Singapore"


def get_local_time(date: datetime) -> datetime:
    target_timezone = pytz.timezone(CURRENT_TIMEZONE)
    timestamp_utc8 = date.astimezone(target_timezone)
    return timestamp_utc8


class MessageStore:
    messages: list[Message] = []

    def store(self, update: Update, context: Application) -> None:
        if message := update.message:
            self.messages.append(message)


def get_date_display(date: datetime) -> str:
    return f"Report date: {date.strftime('%d/%m/%Y')}"


def get_banner_display() -> str:
    return f"=================================="


def get_ledger_entry_display(message: Message) -> str:
    return f"{get_local_time(message.date).strftime('%H:%M:%S')} | {message.from_user.username} | {message.text}"


def get_ledger_display(messages: list[Message]) -> str:
    ledger_entries = [get_ledger_entry_display(message) for message in messages]
    ledger_display_header = "Time | Username | Payment"
    ledger = [ledger_display_header, *ledger_entries]
    return "\n".join(ledger)


@dataclass
class LedgerSummary:
    username: str
    payment: list[str]

    def __str__(self):
        try:
            total_payment = sum(int(i) for i in self.payment)
            return f"{self.username} | {total_payment}"
        except Exception:
            return f"{self.username} | Unable to parse payments"


def get_ledger_summary(messages: list[Message]) -> list[LedgerSummary]:
    ledger_summary: list[LedgerSummary] = []
    usernames = list({message.from_user.username for message in messages})
    for username in usernames:
        payment = [
            message.text
            for message in messages
            if message.from_user.username == username
        ]
        ledger_summary.append(LedgerSummary(username=username, payment=payment))
    return ledger_summary


def get_ledger_summary_display(messages: list[Message]) -> str:
    ledger_summary_header = "Username | Payment"
    ledger_summary = [str(i) for i in get_ledger_summary(messages)]
    ledger = [ledger_summary_header, *ledger_summary]
    return "\n".join(ledger)


def get_display(messages: list[Message], date: datetime = datetime.today()) -> str:
    messages_by_date = [
        i for i in messages if get_local_time(i.date).date() == date.date()
    ]
    banner_display = get_banner_display()
    date_display = get_date_display(date)
    ledger_display = get_ledger_display(messages_by_date)
    ledger_summary_display = get_ledger_summary_display(messages_by_date)

    return f"{banner_display}\n{date_display}\n{banner_display}\n\n{ledger_display}\n\n{ledger_summary_display}"


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


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


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
