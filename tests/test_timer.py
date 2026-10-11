"""Tests for timer formatting logic."""

from datetime import date, timedelta

from app.model import Event
from app.timer import compute_row, format_countdown


# ----------------------------- format_countdown
def test_format_positive():
    assert format_countdown(timedelta(days=5, hours=3, minutes=4, seconds=2)) == "05:03:04:02"


def test_format_negative():
    assert format_countdown(timedelta(days=-1)) == "-01:00:00:00"


def test_format_zero():
    assert format_countdown(timedelta()) == "00:00:00:00"


# ----------------------------- compute_row
def test_compute_row_future():
    ev = Event(label="Future", target_date="2099-01-01")
    status, count = compute_row(ev)
    assert status == "Remaining"
    assert count.startswith("-") is False  # positive (no minus sign)


def test_compute_row_past():
    ev = Event(label="Past", target_date="2000-01-01")
    status, count = compute_row(ev)
    assert status == "Elapsed"
    assert count.startswith("-")


def test_compute_row_today():
    ev = Event(label="Today", target_date=date.today().isoformat())
    status, _ = compute_row(ev)
    assert status == "Today"
