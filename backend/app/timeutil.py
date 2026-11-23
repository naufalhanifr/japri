from datetime import date, datetime, time, timedelta, timezone

WIB = timezone(timedelta(hours=7), "WIB")
_DB_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0)


def to_db(dt):
    if dt.tzinfo is None:
        raise ValueError("waktu harus punya zona waktu")
    return dt.astimezone(timezone.utc).strftime(_DB_FORMAT)


def from_db(text):
    return datetime.strptime(text, _DB_FORMAT).replace(tzinfo=timezone.utc)


def to_wib_iso(value):
    dt = from_db(value) if isinstance(value, str) else value
    if dt.tzinfo is None:
        raise ValueError("waktu harus punya zona waktu")
    return dt.astimezone(WIB).isoformat(timespec="seconds")


def wib_date(dt):
    if dt.tzinfo is None:
        raise ValueError("waktu harus punya zona waktu")
    return dt.astimezone(WIB).date()


def wib_day_range_utc(day: date):
    start = datetime.combine(day, time.min, tzinfo=WIB)
    return start.astimezone(timezone.utc), (start + timedelta(days=1)).astimezone(timezone.utc)
