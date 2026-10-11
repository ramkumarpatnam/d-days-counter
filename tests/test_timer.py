"""Tests for timer formatting logic."""

from datetime import date, datetime, timedelta

from app.model import Event
from app.timer import compute_row, format_calendar_span, format_countdown


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
    status, count = compute_row(ev, datetime(2025, 1, 1, 0, 0, 2))
    assert status == "9132 days ago"
    assert count == "9132:00:00:02"


def test_compute_row_today():
    ev = Event(label="Today", target_date="2025-01-01")
    status, count = compute_row(ev, datetime(2025, 1, 1, 12, 34, 56))
    assert status == "Today"
    assert count == "00:12:34:56"


def test_compute_row_counts_down_to_midnight_by_second():
    ev = Event(label="Future", target_date="2025-01-02")

    assert compute_row(ev, datetime(2025, 1, 1, 23, 59, 58)) == (
        "Remaining", "00:00:00:02"
    )
    assert compute_row(ev, datetime(2025, 1, 1, 23, 59, 59)) == (
        "Remaining", "00:00:00:01"
    )


def test_compute_row_date_argument_uses_start_of_date():
    ev = Event(label="Future", target_date="2025-01-02")

    assert compute_row(ev, date(2025, 1, 1)) == ("Remaining", "01:00:00:00")


def test_calendar_span_counts_calendar_years_months_days_and_time():
    ev = Event(label="Future", target_date="2026-10-11")

    assert format_calendar_span(ev, datetime(2025, 1, 1, 12, 34, 56)) == (
        "01y 09m 09d 11:25:04"
    )


def test_calendar_span_handles_month_end_and_leap_year():
    ev = Event(label="Leap day", target_date="2024-02-29")

    assert format_calendar_span(ev, datetime(2023, 2, 28)) == (
        "01y 00m 01d 00:00:00"
    )


def test_calendar_span_for_past_event_uses_absolute_calendar_span():
    ev = Event(label="Past", target_date="2000-01-01")

    assert format_calendar_span(ev, datetime(2025, 1, 1, 0, 0, 2)) == (
        "25y 00m 00d 00:00:02"
    )


def test_calendar_span_invalid_date_returns_placeholder():
    ev = Event(label="Invalid", target_date="not-a-date")

    assert format_calendar_span(ev, datetime(2025, 1, 1)) == "--"
