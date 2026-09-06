from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

def parse_iso_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

def to_date(value):
    if value is None:
        return None

    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    raise ValueError(f"Invalid date value: {value}")


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def to_utc_naive(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None

    return dt.astimezone(timezone.utc).replace(tzinfo=None)