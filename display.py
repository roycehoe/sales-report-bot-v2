from dataclasses import dataclass
from datetime import datetime
from telegram import Message

from utils import get_local_time


def get_date_display(date: datetime) -> str:
    return f"Report date: {date.strftime('%d/%m/%Y')}"


def get_banner_display() -> str:
    return f"=================================="


def get_ledger_entry_display(message: Message) -> str:
    return f"{get_local_time(message.date).strftime('%H:%M:%S')} | {message.from_user.username} | {message.caption}"


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
            total_payment = sum(int(i) for i in self.payment if i.isdigit())
            return f"{self.username} | {total_payment}"
        except Exception:
            return f"{self.username} | Unable to parse payments"


def get_ledger_summary(messages: list[Message]) -> list[LedgerSummary]:
    ledger_summary: list[LedgerSummary] = []
    usernames = list({message.from_user.username for message in messages})
    for username in usernames:
        payment = [
            message.caption
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


def get_daily_total(messages: list[Message]) -> str:
    try:
        total = [
            int(message.caption)
            for message in messages
            if message.caption is not None and message.caption.isdigit()
        ]
        return str(sum(total))
    except Exception:
        return "Unable to parse payments"


def get_display(messages: list[Message], date: datetime) -> str:
    messages_by_date = [
        i for i in messages if get_local_time(i.date).date() == date.date()
    ]
    banner_display = get_banner_display()
    date_display = get_date_display(date)
    ledger_display = get_ledger_display(messages_by_date)
    ledger_summary_display = get_ledger_summary_display(messages_by_date)
    daily_total = get_daily_total(messages_by_date)

    return f"{banner_display}\n{date_display}\n{banner_display}\n\n{ledger_display}\n\n{ledger_summary_display}\n\nTotal: {daily_total}"
