import asyncio
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from textual.app import App
from textual.widgets import Button, Input, RadioButton, RadioSet, Static

from tko.game.feedback import Feedback
from tko.game.task import Task
from tko.game.task_config import TaskConfig
from tko.game.task_enums import EvalMode
from tko.ui_textual.dialogs import GradeDialog, GradeResult, PercentageSlider, StudyTimeSlider
from tko.ui_textual.app import TkoApp
from tko.ui_textual.tester_app import TkoTesterApp


class _Resolver:
    def __init__(self, folder: Path):
        self.folder = folder

    def target_folder(self, _task: object) -> Path:
        return self.folder


def _task(mode: EvalMode = EvalMode.SELF) -> Task:
    task = Task()
    task.config = TaskConfig(mode)
    task.info.rate = 40
    task.info.study = 5
    return task


def _feedback(folder: Path, task: Task) -> Feedback:
    repo = SimpleNamespace(task_resolver=_Resolver(folder))
    return Feedback(cast(Any, repo), task)


def _feedback_editor(dialog: GradeDialog, field: str) -> Input:
    return dialog.query_one(f"#feedback-{field}", Input)


def _set_feedback_text(dialog: GradeDialog, field: str, value: str) -> None:
    _feedback_editor(dialog, field).value = value


def _feedback_text(dialog: GradeDialog, field: str) -> str:
    return _feedback_editor(dialog, field).value


def test_grade_dialog_validates_and_returns_form_values(tmp_path: Path) -> None:
    task = _task()
    results: list[GradeResult | None] = []

    class GradeApp(App[None]):
        def on_mount(self) -> None:
            self.push_screen(GradeDialog(task, _feedback(tmp_path, task)), results.append)

    async def exercise() -> None:
        app = GradeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dialog = app.screen
            assert isinstance(dialog, GradeDialog)
            assert app.focused is dialog.query_one("#grade-slider", PercentageSlider)
            assert all(_feedback_editor(dialog, field).size.height > 0 for field in Feedback.FIELDS)
            assert dialog.query_one("#grade-confirm", Button).disabled
            assert dialog.query_one("#feedback-label-what", Static).has_class("missing-required")
            dialog.query_one("#grade-slider", PercentageSlider).set_value(45, emit=True)
            await pilot.pause()
            assert dialog.query_one("#grade-slider", PercentageSlider).value == 45
            dialog.query_one("#grade-slider", PercentageSlider).focus()
            await pilot.press("right")
            await pilot.pause()
            assert str(dialog.query_one("#grade-rate", Static).render()) == "50%"
            dialog.query_one("#grade-study-slider", StudyTimeSlider).set_minutes(20, emit=True)
            for field in Feedback.FIELDS:
                _set_feedback_text(dialog, field, field)
            await pilot.pause()
            assert not dialog.query_one("#grade-confirm", Button).disabled
            assert not dialog.query_one("#feedback-label-what", Static).has_class("missing-required")
            dialog._submit()
            await pilot.pause()
            assert results == [GradeResult(50, 20, False, {field: field for field in Feedback.FIELDS})]

    asyncio.run(exercise())


def test_automated_grade_is_readonly(tmp_path: Path) -> None:
    task = _task(EvalMode.DIFF)

    class GradeApp(App[None]):
        def on_mount(self) -> None:
            self.push_screen(GradeDialog(task, _feedback(tmp_path, task)))

    async def exercise() -> None:
        app = GradeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            assert str(app.screen.query_one("#grade-rate", Static).render()) == "40%"
            assert app.screen.query_one("#grade-slider", PercentageSlider).disabled
            assert app.focused is app.screen.query_one("#grade-study-slider", StudyTimeSlider)

    asyncio.run(exercise())


def test_study_time_slider_snaps_and_displays_hours_minutes(tmp_path: Path) -> None:
    task = _task()
    task.info.study = 33

    class GradeApp(App[None]):
        def on_mount(self) -> None:
            self.push_screen(GradeDialog(task, _feedback(tmp_path, task)))

    async def exercise() -> None:
        app = GradeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            slider = app.screen.query_one("#grade-study-slider", StudyTimeSlider)
            assert slider.minutes == 30
            assert str(app.screen.query_one("#grade-study", Static).render()) == "0h30"
            slider.focus()
            await pilot.press("right")
            await pilot.pause()
            assert slider.minutes == 45
            assert str(app.screen.query_one("#grade-study", Static).render()) == "0h45"
            await pilot.press("end")
            await pilot.pause()
            assert slider.minutes == 600
            assert str(app.screen.query_one("#grade-study", Static).render()) == "10h00"

    asyncio.run(exercise())


def test_form_navigation_uses_enter_tab_and_vertical_arrows(tmp_path: Path) -> None:
    task = _task()

    class GradeApp(App[None]):
        def on_mount(self) -> None:
            self.push_screen(GradeDialog(task, _feedback(tmp_path, task)))

    async def exercise() -> None:
        app = GradeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dialog = app.screen
            assert isinstance(dialog, GradeDialog)
            assert app.focused is dialog.query_one("#grade-slider", PercentageSlider)
            await pilot.press("enter")
            assert app.focused is dialog.query_one("#grade-study-slider", StudyTimeSlider)
            await pilot.press("down")
            assert app.focused is dialog.query_one("#grade-mode", RadioSet)
            await pilot.press("up")
            assert app.focused is dialog.query_one("#grade-study-slider", StudyTimeSlider)
            await pilot.press("tab")
            assert app.focused is dialog.query_one("#grade-mode", RadioSet)
            await pilot.press("shift+tab")
            assert app.focused is dialog.query_one("#grade-study-slider", StudyTimeSlider)

    asyncio.run(exercise())


def test_feedback_fields_follow_mode_and_completion_rate(tmp_path: Path) -> None:
    task = _task()

    class GradeApp(App[None]):
        def on_mount(self) -> None:
            self.push_screen(GradeDialog(task, _feedback(tmp_path, task)))

    async def exercise() -> None:
        app = GradeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dialog = app.screen
            assert isinstance(dialog, GradeDialog)

            def enabled(field: str) -> bool:
                return not _feedback_editor(dialog, field).disabled

            assert all(enabled(field) for field in Feedback.FIELDS)
            dialog.query_one("#grade-boss-mode", RadioButton).value = True
            dialog._refresh_form_state()
            assert enabled("what") and enabled("learned")
            assert not enabled("how") and not enabled("tools")
            assert _feedback_text(dialog, "how") == "---"
            assert _feedback_text(dialog, "tools") == "---"

            dialog.query_one("#grade-slider", PercentageSlider).set_value(100, emit=True)
            dialog._refresh_form_state()
            assert enabled("learned")
            assert not enabled("what") and not enabled("how") and not enabled("tools")
            assert _feedback_text(dialog, "what") == "---"

            dialog.query_one("#grade-boss-mode", RadioButton).value = False
            dialog.query_one("#grade-study-mode", RadioButton).value = True
            dialog._refresh_form_state()
            assert not enabled("what")
            assert enabled("how") and enabled("tools") and enabled("learned")
            assert _feedback_text(dialog, "how") == ""
            assert _feedback_text(dialog, "tools") == ""

    asyncio.run(exercise())


def test_enter_selects_mode_and_advances_to_next_visible_field(tmp_path: Path) -> None:
    task = _task()

    class GradeApp(App[None]):
        def on_mount(self) -> None:
            self.push_screen(GradeDialog(task, _feedback(tmp_path, task)))

    async def exercise() -> None:
        app = GradeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dialog = app.screen
            assert isinstance(dialog, GradeDialog)
            dialog.query_one("#grade-mode", RadioSet).focus()
            await pilot.press("right", "enter")
            await pilot.pause()
            assert dialog.query_one("#grade-boss-mode", RadioButton).value
            assert app.focused is dialog.query_one("#feedback-what", Input)

    asyncio.run(exercise())


def test_hidden_feedback_fields_are_cleared_before_confirmation(tmp_path: Path) -> None:
    task = _task()
    results: list[GradeResult | None] = []

    class GradeApp(App[None]):
        def on_mount(self) -> None:
            self.push_screen(GradeDialog(task, _feedback(tmp_path, task)), results.append)

    async def exercise() -> None:
        app = GradeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dialog = app.screen
            assert isinstance(dialog, GradeDialog)
            for field in Feedback.FIELDS:
                _set_feedback_text(dialog, field, f"resposta {field}")
            dialog.query_one("#grade-slider", PercentageSlider).set_value(100, emit=True)
            dialog.query_one("#grade-boss-mode", RadioButton).value = True
            dialog._refresh_form_state()
            assert not dialog.query_one("#grade-confirm", Button).disabled
            dialog._submit()
            await pilot.pause()

    asyncio.run(exercise())

    assert results == [GradeResult(100, 5, True, {"what": "", "how": "", "tools": "", "learned": "resposta learned"})]


def test_invalid_feedback_is_replaced_on_confirmation(tmp_path: Path) -> None:
    task = _task()
    feedback = _feedback(tmp_path, task)
    results: list[GradeResult | None] = []
    path = tmp_path / "src" / "feedback.toml"
    path.parent.mkdir(parents=True)
    path.write_text("what = [", encoding="utf-8")

    class GradeApp(App[None]):
        def on_mount(self) -> None:
            self.push_screen(GradeDialog(task, feedback), results.append)

    async def exercise() -> None:
        app = GradeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dialog = app.screen
            assert isinstance(dialog, GradeDialog)
            assert "será substituído" in str(dialog.query_one("#grade-error").render())
            assert dialog.query_one("#grade-confirm", Button).disabled
            for field in Feedback.FIELDS:
                _set_feedback_text(dialog, field, field)
            await pilot.pause()
            assert not dialog.query_one("#grade-confirm", Button).disabled
            dialog._submit()
            await pilot.pause()

    asyncio.run(exercise())
    assert results == [GradeResult(40, 5, False, {field: field for field in Feedback.FIELDS})]
    result = results[0]
    assert isinstance(result, GradeResult)
    feedback.save_fields(result.fields)
    assert feedback.load_fields() == {field: field for field in Feedback.FIELDS}


def test_cancelled_dialog_does_not_save_feedback(tmp_path: Path) -> None:
    task = _task()
    feedback = _feedback(tmp_path, task)
    results: list[GradeResult | None] = []

    class GradeApp(App[None]):
        def on_mount(self) -> None:
            self.push_screen(GradeDialog(task, feedback), results.append)

    async def exercise() -> None:
        app = GradeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            app.screen.action_cancel()
            await pilot.pause()

    asyncio.run(exercise())

    assert results == [None]
    assert not (tmp_path / "src" / "feedback.toml").exists()
    assert task.info.feedback is False


def test_play_save_records_feedback_task_info_and_log(tmp_path: Path) -> None:
    task = _task()
    saved_logs: list[object] = []
    repo = SimpleNamespace(task_resolver=_Resolver(tmp_path), logger=SimpleNamespace(store=saved_logs.append))
    feedback = Feedback(cast(Any, repo), task)
    app = SimpleNamespace(repo=repo, refresh_view=lambda: None, notify=lambda *_args, **_kwargs: None, _t=lambda pt, _en: pt)
    result = GradeResult(70, 35, True, {field: f"texto {field}" for field in Feedback.FIELDS})

    TkoApp._save_self_evaluation(cast(Any, app), task, feedback, result)

    assert task.info.rate == 70
    assert task.info.study == 35
    assert task.info.boss is True
    assert task.info.feedback is True
    assert feedback.load_fields() == result.fields
    assert len(saved_logs) == 1
    assert saved_logs[0].get_info().get_kv() == task.info.get_kv()


def test_tester_without_repository_warns_instead_of_opening_grade() -> None:
    notifications: list[tuple[tuple[object, ...], dict[str, object]]] = []
    app = SimpleNamespace(repo=None, notify=lambda *args, **kwargs: notifications.append((args, kwargs)))

    TkoTesterApp.action_self_evaluate(cast(Any, app))

    assert notifications[0][0] == ("Não há repositório para registrar a autoavaliação.",)
    assert notifications[0][1]["severity"] == "warning"
