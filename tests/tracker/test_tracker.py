import json
from pathlib import Path

import pytest

from tko.logger.tracker import Track, Tracker
from tko.logger.old_log_loader import TrackerLoader
from tko.logger.versions_writer import VersionsWriter
from tko.util.console import Console


def test_tracker_stores_versions_as_jsonl(tmp_path: Path) -> None:
    source = tmp_path / "solver.py"
    source.write_text("print(1)\n", encoding="utf-8")
    track_folder = tmp_path / ".tko" / "track" / "disc@task01"

    tracker = Tracker().set_folder(track_folder).set_files([source]).set_result("100")

    changed, total_lines = tracker.store()
    assert changed is True
    assert total_lines == 1

    history_file = track_folder / "solver.py.jsonl"
    assert history_file.exists()
    assert not (track_folder / "solver.py.json").exists()
    assert (track_folder / Tracker.log_file).exists()
    tracks: list[Track] = Tracker.load_from_log(str(track_folder / Tracker.log_file))
    record: object = json.loads((track_folder / Tracker.log_file).read_text(encoding="utf-8"))
    assert record == {"timestamp": tracks[0].timestamp, "result": "100", "files": tracks[0].file_stamp_list}
    assert "track" not in TrackerLoader.load_file_versions(str(track_folder))

    history = VersionsWriter().load_history(history_file)
    assert history.count == 1
    assert history.current == "print(1)\n"


def test_tracker_does_not_duplicate_unchanged_jsonl_version(tmp_path: Path) -> None:
    source = tmp_path / "solver.py"
    source.write_text("print(1)\n", encoding="utf-8")
    track_folder = tmp_path / ".tko" / "track" / "disc@task01"

    tracker = Tracker().set_folder(track_folder).set_files([source]).set_result("100")
    assert tracker.store() == (True, 1)
    assert tracker.store() == (False, 1)

    history_file = track_folder / "solver.py.jsonl"
    history = VersionsWriter().load_history(history_file)
    assert history.count == 1

    rows = (track_folder / Tracker.log_file).read_text(encoding="utf-8").splitlines()
    assert len(rows) == 2


def test_tracker_skips_conflicted_file_and_keeps_valid_versions(tmp_path: Path) -> None:
    bad_source: Path = tmp_path / "bad.py"
    good_source: Path = tmp_path / "good.py"
    bad_source.write_text("print(1)\n", encoding="utf-8")
    good_source.write_text("print(2)\n", encoding="utf-8")
    track_folder: Path = tmp_path / "track"
    track_folder.mkdir()
    bad_history: Path = track_folder / "bad.py.jsonl"
    original: bytes = b'<<<<<<< HEAD\n{}\n=======\n{}\n>>>>>>> origin/main\n'
    bad_history.write_bytes(original)
    warnings: list[str] = []
    tracker: Tracker = Tracker(on_warning=warnings.append)
    tracker.set_folder(track_folder).set_files([bad_source, good_source]).set_result("100")

    assert tracker.store() == (True, 1)
    assert bad_history.read_bytes() == original
    assert VersionsWriter().load_history(track_folder / "good.py.jsonl").current == "print(2)\n"
    assert len(warnings) == 1
    assert f"{bad_history}:2" in warnings[0]
    assert "Git" in warnings[0]
    tracks = Tracker.load_from_log(str(track_folder / Tracker.log_file))
    assert len(tracks) == 1
    assert tracks[0].result == "100"
    assert len(tracks[0].file_stamp_list) == 1
    assert tracks[0].file_stamp_list[0].startswith("good.py:")


def test_tracker_warns_on_terminal_when_all_histories_are_invalid(tmp_path: Path) -> None:
    source: Path = tmp_path / "solver.py"
    source.write_text("print(1)\n", encoding="utf-8")
    history: Path = tmp_path / "solver.py.jsonl"
    history.write_text('{"ts":\n', encoding="utf-8")
    tracker: Tracker = Tracker().set_folder(tmp_path).set_files([source]).set_result("0")
    with Console.capture(stderr=True) as captured:
        assert tracker.store() == (False, 0)
    assert str(history) in captured.getvalue()
    assert "solver.py:" not in (tmp_path / Tracker.log_file).read_text(encoding="utf-8")


def test_tracker_rejects_invalid_jsonl_with_file_and_line(tmp_path: Path) -> None:
    path: Path = tmp_path / Tracker.log_file
    path.write_text('{"timestamp":"2026-09-14_10-00-00","result":"100","files":[]}\n{"timestamp":\n', encoding="utf-8")
    with pytest.raises(ValueError, match=r"track.jsonl:2:"):
        Tracker.load_from_log(str(path))
