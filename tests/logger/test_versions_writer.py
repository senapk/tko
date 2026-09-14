from datetime import datetime
import json
from pathlib import Path

import pytest

from tko.logger.versions_writer import AuditElement, InvalidHistoryError, VersionsWriter


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


@pytest.mark.parametrize("invalid_line", [
    '{"ts":', '{}', 'null', '[]', '',
])
def test_invalid_history_is_preserved_and_not_cached(tmp_path: Path, invalid_line: str) -> None:
    audit_file: Path = tmp_path / "solver.py.jsonl"
    VersionsWriter().write(audit_file, "print(1)\n")
    valid_bytes: bytes = audit_file.read_bytes()
    original: bytes = valid_bytes + (invalid_line + "\n").encode("utf-8")
    audit_file.write_bytes(original)
    writer: VersionsWriter = VersionsWriter()

    with pytest.raises(InvalidHistoryError) as raised:
        writer.write(audit_file, "print(2)\n")

    assert raised.value.path == audit_file
    assert raised.value.line_number == 2
    assert raised.value.reason
    assert str(audit_file) in str(raised.value)
    assert raised.value.__cause__ is not None
    assert audit_file.read_bytes() == original
    assert audit_file not in writer.histories

    # A repaired history can be retried with the same writer.
    audit_file.write_bytes(valid_bytes)
    assert writer.write(audit_file, "print(2)\n")
    assert [snapshot.content for snapshot in writer.load_history(audit_file).snapshots] == [
        "print(1)\n", "print(2)\n",
    ]


def test_legacy_plain_text_snapshot_accepts_new_diff(tmp_path: Path) -> None:
    audit_file: Path = tmp_path / "legacy.py.jsonl"
    content: str = "print('ação')\n"
    entry: AuditElement = AuditElement(
        timestamp=datetime(2026, 6, 10), hash_value=VersionsWriter._hash(content),
        mode="full", content=content,
    )
    audit_file.write_text(entry.to_jsonl_line() + "\n", encoding="utf-8")
    writer: VersionsWriter = VersionsWriter()
    assert writer.write(audit_file, content) is False
    assert writer.write(audit_file, "print('nova ação')\n")
    assert [snapshot.content for snapshot in writer.load_history(audit_file).snapshots] == [
        content, "print('nova ação')\n",
    ]


@pytest.mark.parametrize("newline", [b"\n", b"\r\n"])
def test_git_conflict_accepts_both_entries_in_original_order(tmp_path: Path, newline: bytes) -> None:
    audit_file: Path = tmp_path / "solver.py.jsonl"
    local: bytes = AuditElement(
        timestamp=datetime(2026, 9, 14), hash_value=VersionsWriter._hash("local\n"),
        mode="full", content="local\n",
    ).to_jsonl_line().encode("utf-8") + newline
    remote: bytes = AuditElement(
        timestamp=datetime(2026, 9, 13), hash_value=VersionsWriter._hash("remote\n"),
        mode="full", content="remote\n",
    ).to_jsonl_line().encode("utf-8") + newline
    original: bytes = newline.join([b"<<<<<<< HEAD", local.rstrip(b"\r\n"), b"=======",
                                    remote.rstrip(b"\r\n"), b">>>>>>> origin/main", b""])
    # Multiple conflicts and repeated snapshots must preserve all entries.
    audit_file.write_bytes(original + original)
    writer: VersionsWriter = VersionsWriter()
    history = writer.load_history(audit_file)
    assert [snapshot.content for snapshot in history.snapshots] == ["local\n", "remote\n"] * 2
    assert audit_file.read_bytes() == (local + remote) * 2
    assert writer.load_history(audit_file).count == 4
    assert writer.write(audit_file, "new version\n")
    assert VersionsWriter().load_history(audit_file).current == "new version\n"


def test_conflict_with_invalid_json_keeps_original_file(tmp_path: Path) -> None:
    audit_file: Path = tmp_path / "solver.py.jsonl"
    original: bytes = b'<<<<<<< HEAD\n{}\n=======\nnull\n>>>>>>> origin/main\n'
    audit_file.write_bytes(original)
    with pytest.raises(InvalidHistoryError) as raised:
        VersionsWriter().load_history(audit_file)
    assert raised.value.line_number == 2
    assert audit_file.read_bytes() == original
