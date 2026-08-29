from pathlib import Path

from tko.logger.tracker import Tracker
from tko.logger.versions_writer import VersionsWriter


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
