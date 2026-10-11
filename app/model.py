"""Data model: event definitions and JSON persistence."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional


@dataclass
class Event:
    """A single countdown/event target."""
    label: str
    target_date: str                 # ISO date string YYYY-MM-DD
    color: str = "blue"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    # ------------------------------------------------------------------
    # convenience helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_date(cls, label: str, target: date) -> "Event":
        return cls(label=label, target_date=target.isoformat())

    def parse_target_date(self) -> date:
        return date.fromisoformat(self.target_date)

    def delta(self, now: Optional[date] = None) -> Optional[timedelta]:
        """Return target - now. None if the date is invalid."""
        now = now or datetime.now().date()
        try:
            return self.parse_target_date() - now
        except ValueError:
            return None

    @property
    def status(self) -> str:
        """'Elapsed' for past dates, 'Remaining' for future dates."""
        d = self.delta()
        if d is None:
            return "Invalid"
        return "Elapsed" if d.days < 0 else ("Today" if d.days == 0 else "Remaining")


class EventStore:
    """Handle loading / saving the event list to JSON."""

    def __init__(self, path: Path):
        self.path = Path(path)

    # ------------------------------------------------------------------
    # persistence
    # ------------------------------------------------------------------
    def load(self) -> List[Event]:
        """Load events from JSON file. Returns [] if file missing/corrupt."""
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        return [Event(**item) for item in raw if isinstance(item, dict)]

    def save(self, events: List[Event]) -> None:
        """Persist events to JSON, creating directories as needed."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([asdict(e) for e in events], indent=2),
            encoding="utf-8",
        )
