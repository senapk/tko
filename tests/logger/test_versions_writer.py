from datetime import datetime
import json
from pathlib import Path

from tko.logger.versions_writer import VersionsWriter


def test_versions_writer_reloads_full_and_diff_snapshots(tmp_path: Path) -> None:
    audit_file = tmp_path / "solver.py.jsonl"
    writer = VersionsWriter(n_diffs=2)

    assert writer.write(audit_file, "print(1)\n", datetime(2026, 6, 10, 14, 0, 0)) is True
    assert writer.write(audit_file, "print(2)\n", datetime(2026, 6, 10, 14, 1, 0)) is True
    assert writer.write(audit_file, "print(3)\n", datetime(2026, 6, 10, 14, 2, 0)) is True
    assert writer.write(audit_file, "print(3)\n", datetime(2026, 6, 10, 14, 3, 0)) is False

    lines = audit_file.read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["mode"] for line in lines] == ["full", "diff", "full"]

    history = VersionsWriter().load_history(audit_file)

    assert [snapshot.content for snapshot in history.snapshots] == [
        "print(1)\n",
        "print(2)\n",
        "print(3)\n",
    ]

