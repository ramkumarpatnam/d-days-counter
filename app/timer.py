"""Timer logic: format deltas and classify events."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional, Tuple

from app.model import Event


def get_now() -> date:
    """Wrapper so tests can monkeypatch if needed."""
    return datetime.now().date()


def format_countdown(delta: timedelta) -> str:
    """Format a timedelta as DD:HH:MM:SS (abs value)."""
    total = int(delta.total_seconds())
    sign = "-" if total < 0 else ""
    total = abs(total)
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{sign}{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"


def compute_row(event: Event, now: Optional[date] = None) -> Tuple[str, str]:
    """Return (status, formatted_count) for an event."""
    now = now or get_now()
    d = event.delta(now)
    if d is None:
        return ("Invalid", "00:00:00:00")
    status = "Elapsed" if d.days < 0 else ("Today" if d.days == 0 else "Remaining")
    return (status, format_countdown(d))
