from datetime import date, datetime
from zoneinfo import ZoneInfo

def parse_iso_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
