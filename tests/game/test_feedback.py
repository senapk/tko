from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from tko.game.feedback import FEEDBACK_TOML, Feedback, FeedbackStatus


class _Resolver:
    def __init__(self, folder: Path | None):
        self.folder = folder

    def target_folder(self, _task: object) -> Path | None:
        return self.folder


def _feedback(folder: Path | None) -> Feedback:
    repo = SimpleNamespace(task_resolver=_Resolver(folder))
    return Feedback(cast(Any, repo), cast(Any, object()))


def test_ensure_feedback_file_creates_template(tmp_path: Path) -> None:
    feedback = _feedback(tmp_path)

    assert feedback.ensure_feedback_file() is True

    path = tmp_path / "src" / "feedback.toml"
    assert path.read_text() == FEEDBACK_TOML


def test_ensure_feedback_file_does_not_overwrite_existing_file(tmp_path: Path) -> None:
    path = tmp_path / "src" / "feedback.toml"
    path.parent.mkdir(parents=True)
    path.write_text("changed")
    feedback = _feedback(tmp_path)

    assert feedback.ensure_feedback_file() is True

    assert path.read_text() == "changed"


def test_get_feedback_status_returns_not_filled_for_initial_template(tmp_path: Path) -> None:
    feedback = _feedback(tmp_path)
    feedback.ensure_feedback_file()

    assert feedback.get_feedback_status() == (FeedbackStatus.NOT_FILLED, 4)


def test_get_feedback_status_returns_filled_for_completed_content(tmp_path: Path) -> None:
    feedback = _feedback(tmp_path)
    feedback.ensure_feedback_file()
    (tmp_path / "src" / "feedback.toml").write_text(
        'what = "feito"\n'
        'how = "sozinho"\n'
        'tools = "editor"\n'
        'learned = "conteudo"\n'
    )

    assert feedback.get_feedback_status() == (FeedbackStatus.FILLED, 0)


def test_feedback_returns_false_when_task_has_no_folder() -> None:
    feedback = _feedback(None)

    assert feedback.ensure_feedback_file() is False
    assert feedback.get_feedback_status() == (FeedbackStatus.NOT_FILLED, 4)
