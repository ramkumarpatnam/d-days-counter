"""Tests for the data model and persistence."""

import json
from datetime import date, timedelta, datetime
from pathlib import Path

import pytest

from app.model import Event, EventStore


# ------------------------------------------------------------------ Event
def test_event_defaults():
    ev = Event(label="Birthday", target_date="2025-01-01")
    assert ev.label == "Birthday"
    assert ev.target_date == "2025-01-01"
    assert ev.id  # non-empty uuid
    assert ev.created_at  # set


def test_event_from_date():
    ev = Event.from_date("Launch", date(2025, 6, 15))
    assert ev.target_date == "2025-06-15"


def test_event_parse_target_date():
    ev = Event(label="X", target_date="2030-12-25")
    assert ev.parse_target_date() == date(2030, 12, 25)


def test_event_status_future():
    ev = Event(label="Future", target_date="2099-01-01")
    assert ev.status == "Remaining"


def test_event_status_past():
    ev = Event(label="Past", target_date="2000-01-01")
    assert ev.status == "Elapsed"


def test_event_status_today():
    ev = Event(label="Today", target_date=datetime.now().date().isoformat())
    assert ev.status == "Today"


def test_event_delta_past():
    ev = Event(label="Past", target_date="2000-01-01")
    d = ev.delta()
    assert d is not None
    assert d.days < 0


# ------------------------------------------------------- EventStore
def test_store_load_missing_returns_empty(tmp_path: Path):
    store = EventStore(tmp_path / "events.json")
    assert store.load() == []


def test_store_load_corrupt_returns_empty(tmp_path: Path):
    f = tmp_path / "events.json"
    f.write_text("not json{")
    store = EventStore(f)
    assert store.load() == []


def test_store_save_then_load_roundtrip(tmp_path: Path):
    store = EventStore(tmp_path / "events.json")
    events = [
        Event(label="Past", target_date="2000-01-01"),
        Event(label="Future", target_date="2099-12-31"),
    ]
    store.save(events)
    loaded = store.load()
    assert len(loaded) == 2
    assert loaded[0].label == "Past"
    assert loaded[0].target_date == "2000-01-01"
    assert loaded[1].label == "Future"


def test_store_save_creates_directory(tmp_path: Path):
    store = EventStore(tmp_path / "subdir" / "events.json")
    store.save([Event(label="X", target_date="2025-01-01")])
    assert store.path.exists()
