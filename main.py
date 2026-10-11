"""Entry point for the Days Counter application."""

import sys
from pathlib import Path
from app.model import EventStore
from app.ui import MainWindow


def main() -> None:
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    store = EventStore(data_dir / "events.json")
    app = MainWindow(store)
    app.run()


if __name__ == "__main__":
    main()