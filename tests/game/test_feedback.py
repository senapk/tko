from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

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


def test_save_and_load_fields_uses_canonical_toml(tmp_path: Path) -> None:
    feedback = _feedback(tmp_path)
    fields = {
        "what": "Resolvi os exercícios.",
        "how": "Em dupla.",
        "tools": "Editor e IA para revisar.",
        "learned": "Estruturas de repetição.",
    }

    feedback.save_fields(fields)

    assert feedback.load_fields() == fields
    assert feedback.get_feedback_status() == (FeedbackStatus.FILLED, 0)
    assert (tmp_path / "src" / "feedback.toml").read_text(encoding="utf-8").splitlines() == [
        'what = "Resolvi os exercícios."',
        'how = "Em dupla."',
        'tools = "Editor e IA para revisar."',
        'learned = "Estruturas de repetição."',
    ]


def test_load_fields_rejects_invalid_toml(tmp_path: Path) -> None:
    feedback = _feedback(tmp_path)
    path = tmp_path / "src" / "feedback.toml"
    path.parent.mkdir(parents=True)
    path.write_text("what = [", encoding="utf-8")

    with pytest.raises(ValueError, match="TOML inválido"):
        feedback.load_fields()

    assert feedback.get_feedback_status() == (FeedbackStatus.INVALID, 4)


def test_feedback_status_uses_only_fields_required_by_mode_and_completion(tmp_path: Path) -> None:
    task = SimpleNamespace(info=SimpleNamespace(rate=100, boss=True))
    repo = SimpleNamespace(task_resolver=_Resolver(tmp_path))
    feedback = Feedback(cast(Any, repo), cast(Any, task))
    feedback.save_fields({"what": "", "how": "", "tools": "", "learned": "Aprendi."})

    assert feedback.required_fields() == ("learned",)
    assert feedback.get_feedback_status() == (FeedbackStatus.FILLED, 0)

    task.info.boss = False
    feedback.save_fields({"what": "", "how": "Em dupla.", "tools": "Editor.", "learned": "Aprendi."})

    assert feedback.required_fields() == ("how", "tools", "learned")
    assert feedback.get_feedback_status() == (FeedbackStatus.FILLED, 0)
