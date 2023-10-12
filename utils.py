from datetime import datetime
import pytz

CURRENT_TIMEZONE = "Asia/Singapore"


def get_local_time(date: datetime) -> datetime:
    target_timezone = pytz.timezone(CURRENT_TIMEZONE)
    timestamp_utc8 = date.astimezone(target_timezone)
    return timestamp_utc8
