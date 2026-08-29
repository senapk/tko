from types import SimpleNamespace
from typing import Any, cast

from tko.floating.floating_grade import FloatingGrade
from tko.game.feedback import FeedbackStatus
from tko.game.task import Task
from tko.i18n import set_language


class _Info:
    def __init__(self) -> None:
        self.rate = 20
        self.study = 5
        self.feedback = False
        self.boss = False

    def set_study(self, value: str) -> None:
        self.study = int(value)


class _Task:
    def __init__(self) -> None:
        self.config = SimpleNamespace(is_eval_test=False)
        self.info = _Info()


class _Feedback:
    def __init__(self, status: FeedbackStatus, ensured: bool = True):
        self.status = status
        self.ensured = ensured
        self.ensure_calls = 0
        self.status_calls = 0

    def ensure_feedback_file(self) -> bool:
        self.ensure_calls += 1
        return self.ensured

    def get_feedback_status(self) -> tuple[FeedbackStatus, int]:
        self.status_calls += 1
        return self.status, 0


def test_final_enter_keeps_floating_open_when_feedback_is_not_filled() -> None:
    task = _Task()
    feedback = _Feedback(FeedbackStatus.NOT_FILLED)
    opened = 0
    exited: list[Any] = []

    def opener() -> None:
        nonlocal opened
        opened += 1

    floating = FloatingGrade(cast(Any, task), exited.append, cast(Any, feedback), opener)
    floating.line = len(floating.all_input_lines) - 1

    floating.process_input(ord("\n"))

    assert opened == 0
    assert feedback.ensure_calls == 1
    assert feedback.status_calls == 1
    assert floating.is_enable() is True
    assert exited == []
    assert task.info.feedback is False


def test_final_enter_closes_and_stores_task_when_feedback_is_filled() -> None:
    task = _Task()
    feedback = _Feedback(FeedbackStatus.FILLED)
    opened = 0
    exited: list[Any] = []

    def opener() -> None:
        nonlocal opened
        opened += 1

    floating = FloatingGrade(cast(Any, task), exited.append, cast(Any, feedback), opener)
    floating.line = len(floating.all_input_lines) - 1

    floating.process_input(ord("\n"))

    assert opened == 0
    assert feedback.status_calls == 1
    assert floating.is_enable() is False
    assert exited == [task]
    assert task.info.feedback is True


def test_hash_opens_feedback_file_on_demand() -> None:
    task = _Task()
    feedback = _Feedback(FeedbackStatus.NOT_FILLED)
    opened = 0

    def opener() -> None:
        nonlocal opened
        opened += 1

    floating = FloatingGrade(cast(Any, task), feedback=cast(Any, feedback), feedback_opener=opener)

    assert opened == 0

    floating.process_input(ord("#"))

    assert opened == 1
    assert floating.is_enable() is True


def test_final_enter_stays_open_when_feedback_file_cannot_be_created() -> None:
    task = _Task()
    feedback = _Feedback(FeedbackStatus.FILLED, ensured=False)
    exited: list[Any] = []

    floating = FloatingGrade(cast(Any, task), exited.append, cast(Any, feedback), None)
    floating.line = len(floating.all_input_lines) - 1

    floating.process_input(ord("\n"))

    assert feedback.ensure_calls == 1
    assert feedback.status_calls == 0
    assert floating.is_enable() is True
    assert exited == []


def test_update_content_aligns_input_separators_in_english() -> None:
    set_language("en")
    try:
        task = Task()
        task.info.rate = 20
        task.info.study = 5
        feedback = _Feedback(FeedbackStatus.NOT_FILLED)

        floating = FloatingGrade(task, feedback=cast(Any, feedback))
        floating.update_content()

        lines = [line.plain() for line in floating.floating.content[:3]]
        separator_columns = [
            lines[0].index("├"),
            lines[1].index("├"),
            lines[2].index("│"),
        ]

        assert len(set(separator_columns)) == 1
    finally:
        set_language("pt-BR")
