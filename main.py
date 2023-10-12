from dataclasses import dataclass
from datetime import datetime
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
        date: datetime = datetime.today(),
    ):
        return [
            message for message in self.messages if message.date.date() == date.date()
        ]


def get_date_display(date: datetime) -> str:
    return f"Report date: {date.strftime('%d/%m/%Y')}"


def get_banner_display() -> str:
    return f"=================================="


def get_ledger_entry_display(message: Message) -> str:
    return f"{message.date.strftime('%H:%M:%S')} | {message.from_user.username} | {message.text}"


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
            message.text for message in messages if message.from_user == username
        ]
        ledger_summary.append(LedgerSummary(username=username, payment=payment))
    return ledger_summary


def get_ledger_summary_display(messages: list[Message]) -> str:
    ledger_summary_header = "Username | Payment"
    ledger_summary = [str(i) for i in get_ledger_summary(messages)]
    ledger = [ledger_summary_header, *ledger_summary]
    return "\n".join(ledger)


def get_display(messages: list[Message], date: datetime = datetime.today()) -> str:
    banner_display = get_banner_display()
    date_display = get_date_display(date)
    ledger_display = get_ledger_display(messages)
    ledger_summary_display = get_ledger_summary_display(messages)

    return f"{date_display} \n {banner_display} \n {ledger_display} \n {ledger_summary_display}"


class MessageFormatter:
    def __init__(self, message_store: MessageStore):
        self.message_store = message_store

    async def show(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if message := update.message:
            display = get_display(message_store.messages)
            await message.reply_text(f"{display}")
            # await message.reply_text(f"{message_store.messages}")


application = Application.builder().token(TOKEN).build()
message_store = MessageStore()
message_formatter = MessageFormatter(message_store)

message_handler = MessageHandler(filters.Chat(chat_id=CHAT_ID), message_store.store)
application.add_handler(message_handler)
application.add_handler(CommandHandler("show", message_formatter.show))

application.run_polling(allowed_updates=Update.ALL_TYPES)
