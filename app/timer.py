"""Timer logic: format deltas and classify events."""

from __future__ import annotations

import calendar
from datetime import date, datetime, time, timedelta
from typing import Optional, Tuple, Union

from app.model import Event


def get_now() -> datetime:
    """Wrapper so tests can monkeypatch if needed."""
    return datetime.now()


def format_countdown(delta: timedelta) -> str:
    """Format a timedelta as DD:HH:MM:SS (abs value)."""
    total = int(delta.total_seconds())
    sign = "-" if total < 0 else ""
    total = abs(total)
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{sign}{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"


def _add_months(value: datetime, months: int) -> datetime:
    month_index = value.year * 12 + value.month - 1 + months
    year, month_zero_based = divmod(month_index, 12)
    month = month_zero_based + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def format_calendar_span(event: Event, now: Optional[Union[date, datetime]] = None) -> str:
    """Format the absolute event span as calendar years, months, days, and time."""
    now = now or get_now()
    try:
        target_date = event.parse_target_date()
    except ValueError:
        return "--"
    current = now if isinstance(now, datetime) else datetime.combine(now, time.min)
    target = datetime.combine(target_date, time.min)
    start, end = sorted((current, target))

    years = end.year - start.year
    while _add_months(start, years * 12) > end:
        years -= 1
    cursor = _add_months(start, years * 12)

    months = (end.year - cursor.year) * 12 + end.month - cursor.month
    while _add_months(cursor, months) > end:
        months -= 1
    cursor = _add_months(cursor, months)

    days = (end.date() - cursor.date()).days
    while cursor + timedelta(days=days) > end:
        days -= 1
    cursor += timedelta(days=days)

    hours, remainder = divmod(int((end - cursor).total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{years:02d}y {months:02d}m {days:02d}d {hours:02d}:{minutes:02d}:{seconds:02d}"


def compute_row(
    event: Event, now: Optional[Union[date, datetime]] = None
) -> Tuple[str, str]:
    """Return the event status and live time from its target-date midnight."""
    now = now or get_now()
    try:
        target_date = event.parse_target_date()
    except ValueError:
        return ("Invalid", "00:00:00:00")
    if isinstance(now, datetime):
        current = now
    else:
        current = datetime.combine(now, time.min)

    target = datetime.combine(target_date, time.min)
    if target_date < current.date():
        status = f"{(current.date() - target_date).days} days ago"
    elif target_date == current.date():
        status = "Today"
    else:
        status = "Remaining"
    return (status, format_countdown(abs(target - current)))
