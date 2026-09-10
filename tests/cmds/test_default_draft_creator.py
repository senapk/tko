from pathlib import Path

from tko.cmds.default_draft_creator import DefaultDraftCreator
from tko.config.settings import Settings


def test_creates_empty_draft_when_language_has_no_template(tmp_path: Path) -> None:
    draft = DefaultDraftCreator(Settings(None)).create(tmp_path / "src" / "unknown", "unknown")

    assert draft is not None
    assert draft.read_text(encoding="utf-8") == ""


def test_does_not_replace_an_existing_draft(tmp_path: Path) -> None:
    folder = tmp_path / "src" / "py"
    folder.mkdir(parents=True)
    existing = folder / "draft.py"
    existing.write_text("my solution", encoding="utf-8")

    draft = DefaultDraftCreator(Settings(None)).create(folder, "py")

    assert draft is None
    assert existing.read_text(encoding="utf-8") == "my solution"
