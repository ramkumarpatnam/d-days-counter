from pathlib import Path

import main


def test_source_events_file_uses_project_data_directory(monkeypatch):
    monkeypatch.delattr(main.sys, "frozen", raising=False)

    assert main.get_events_file() == Path(main.__file__).parent / "data" / "events.json"


def test_frozen_events_file_uses_appdata(monkeypatch, tmp_path):
    monkeypatch.setattr(main.sys, "frozen", True, raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path))

    assert main.get_events_file() == tmp_path / "DaysCounter" / "events.json"
