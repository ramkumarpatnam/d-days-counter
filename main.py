"""Entry point for the Days Counter application."""

import os
import sys
from pathlib import Path
from app.model import EventStore
from app.ui import MainWindow


def get_events_file() -> Path:
    if getattr(sys, "frozen", False):
        app_data = Path(os.environ.get(
            "APPDATA", Path.home() / "AppData" / "Roaming"
        ))
        return app_data / "DaysCounter" / "events.json"
    return Path(__file__).parent / "data" / "events.json"


def main() -> None:
    store = EventStore(get_events_file())
    app = MainWindow(store)
    app.run()


if __name__ == "__main__":
    main()