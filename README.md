# Days Counter

A simple Windows desktop app (Python + Tkinter) that shows **live countdown / elapsed time** to/from any date you choose.

## Features

- Add multiple labeled events (past or future)
- Real-time DD:HH:MM:SS counter (updates every second)
- Status column: **Remaining**, **Elapsed**, or **Today**
- Persists events to a local JSON file (`data/events.json`)
- No external runtime dependencies — just Python standard library

## Quick Start

```bash
# 1. Clone / download
git clone https://github.com/<your-username>/d-days-counter.git
cd d-days-counter

# 2. Run (Python 3.9+)
python main.py
```

## Project Layout

```
d-days-counter/
├── main.py                 # entry point
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

## Packaging (optional)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole main.py
# produces dist/main.exe
```

## License

MIT