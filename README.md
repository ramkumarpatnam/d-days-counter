# Days Counter

A simple Windows desktop app (Python + Tkinter) that shows **live countdown / elapsed time** to/from any date you choose.

## Features

- Add multiple labeled events (past or future)
- Live DD:HH:MM:SS countdown to midnight at the start of the selected date; past dates show elapsed time from that date
- Built-in calendar date picker, with manual date entry also supported
- Six event color presets that remain saved with each event
- One-click dark theme for the main window, event editor, and calendar
- Dates are entered as `YYYY-MM-DD` (for example, `2026-10-11`)
- Edit and Delete stay beside the event list; double-click or press Enter to edit
- Status column: **Remaining**, **Today**, or the calendar-day age of past events (for example, **12 days ago**)
- Separate live columns for total **days / time** and calendar **years / months / days / time**
- Persists events to a local JSON file (`data/events.json`)
- No external runtime dependencies — just Python standard library

## Quick Start

```bash
# Run from source (Python 3.9+)
python main.py
```

## Build a Windows App

On Windows, double-click `build_windows.bat`. It installs the build dependency,
creates a standalone executable in a versioned `dist\build-*` folder, and updates
the desktop shortcut. Copy that executable anywhere and double-click it to launch
the app; Python does not need to be installed on the computer where it runs.

The packaged app stores its events in
`%APPDATA%\DaysCounter\events.json`, so data persists across launches and is
kept separately from the executable. Running from source continues to use
`data\events.json` in the project folder.

## Project Layout

```
d-days-counter/
├── main.py                 # entry point
├── days_counter.ico        # Windows app and desktop shortcut icon
├── app/
│   ├── model.py            # Event dataclass + JSON store
│   ├── timer.py            # formatting logic
│   └── ui.py               # Tkinter UI
├── tests/
│   ├── test_model.py
│   └── test_timer.py
├── .github/workflows/ci.yml
├── data/events.json        # auto-created
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push/PR:

- Installs Python 3.11
- Runs `pytest`
- Syntax-checks all `.py` files

## Packaging manually

```bash
pip install -r requirements-build.txt
python -m PyInstaller --clean --noconfirm --onefile --windowed --name DaysCounter --icon days_counter.ico --distpath dist\app --workpath build\app main.py
# produces dist\app\DaysCounter.exe
```

## License

MIT