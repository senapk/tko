import asyncio
from pathlib import Path

import pytest
from textual.widgets import Static

from tko.config.settings import Settings
from tko.enums.execution_result import ExecutionResult
from tko.game.task import Task
from tko.game.task_enums import EvalMode
from tko.game.task_location import TaskLocation
from tko.logger.tracker import Tracker
from tko.logger.versions_writer import VersionsWriter
from tko.repository.remote import Source
from tko.repository.repository import Repository
from tko.repository.task_data_format import initialize_task_data
from tko.run.run_config import RunConfig
from tko.run.run_context import RunContext
from tko.run.run_executor import RunExecutor
from tko.run.solver_builder import SolverBuilder
from tko.run.task_resolution_service import TaskResolutionService
from tko.tester.tester_state import SeqMode
from tko.ui_textual.tester_app import TkoTesterApp
from tko.util.console import Console


def _context(tmp_path: Path) -> RunContext:
    settings: Settings = Settings(tmp_path / "settings")
    settings.rs.changedir = tmp_path
    settings.app.use_images = False
    repo: Repository = Repository(tmp_path, settings.rs, None, recursive_search=False)
    index: Path = tmp_path / "README.md"
    index.write_text("# Course\n", encoding="utf-8")
    repo.data.set_source(Source.from_local_file("labs", index, is_editable=True))
    task: Task = Task()
    task.basic.source_name = "poo"
    task.basic.key = "labs/relogio"
    task.location = TaskLocation(
        index_path=index, raw_link="poo/labs/relogio/README.md", eval=EvalMode.DIFF,
    )
    repo.game.tasks[task.basic.full_key] = task
    source: Path = tmp_path / "poo/labs/relogio/src/py/draft.py"
    source.parent.mkdir(parents=True)
    source.write_text("print(42)\n", encoding="utf-8")
    cases: Path = tmp_path / "cases.tio"
    cases.write_text(
        ">>>>>>>> INSERT answer\n======== EXPECT\n42\n<<<<<<<< FINISH\n",
        encoding="utf-8",
    )
    ctx: RunContext = RunContext(RunConfig(), settings, [source], None, "py", repo)
    ctx.pwd = source.parent
    ctx.wdir.solver = SolverBuilder([source], settings)
    ctx.wdir.source_list = [cases]
    ctx.wdir.build_unit_list()
    ctx.wdir_builded = True
    initialize_task_data(tmp_path)
    return ctx


def test_resolution_initializes_history_for_discovered_task(tmp_path: Path) -> None:
    ctx: RunContext = _context(tmp_path)
    TaskResolutionService().setup_task(ctx)
    assert ctx.task is not None
    assert ctx.task.basic.full_key == "poo@labs/relogio"
    assert ctx.track_folder == tmp_path / ".tko/track/poo/labs/relogio"


def test_resolution_preserves_explicit_selection(tmp_path: Path) -> None:
    ctx: RunContext = _context(tmp_path)
    assert ctx.repo is not None
    selected: Task = Task()
    selected.basic.source_name = "poo"
    selected.basic.key = "labs/selected"
    ctx.set_task(ctx.repo, selected)
    TaskResolutionService().setup_task(ctx)
    assert ctx.task is selected
    assert ctx.track_folder == tmp_path / ".tko/track/poo/labs/selected"


@pytest.mark.parametrize("inside_repo", [False, True])
def test_standalone_execution_has_no_history(tmp_path: Path, inside_repo: bool) -> None:
    ctx: RunContext = _context(tmp_path)
    ctx.pwd = tmp_path
    if not inside_repo:
        ctx.repo = None
    service: TaskResolutionService = TaskResolutionService()
    service.setup_task(ctx)
    service.setup_task(ctx)
    assert ctx.track_folder is None
    assert ctx.get_task().basic.full_key == "NONE@STANDALONE"
    with Console.capture():
        assert RunExecutor(ctx).run_tests() == 100
    assert not (tmp_path / ".tko/track").exists()


@pytest.mark.parametrize("history_state", ["valid", "conflict", "invalid"])
def test_raw_and_tui_execute_with_shared_history(tmp_path: Path, history_state: str) -> None:
    ctx: RunContext = _context(tmp_path)
    TaskResolutionService().setup_task(ctx)
    assert ctx.track_folder is not None
    history: Path = ctx.track_folder / "src/py/draft.py.jsonl"
    original: bytes = b""
    if history_state != "valid":
        VersionsWriter().write(history, "print(0)\n")
        snapshot: bytes = history.read_bytes()
        original = b"<<<<<<< HEAD\n" + snapshot + b"=======\n" + snapshot + b">>>>>>> origin/main\n"
        if history_state == "invalid":
            original += b'{"ts":\n'
        history.write_bytes(original)

    with Console.capture(stderr=True) as stderr:
        with Console.capture():
            assert RunExecutor(ctx).run_tests() == 100
    assert (str(history) in stderr.getvalue()) is (history_state == "invalid")
    assert ctx.wdir.unit_list[0].result == ExecutionResult.SUCCESS

    async def exercise() -> None:
        if history_state == "conflict":
            # Exercise automatic repair independently in the TUI as well.
            history.write_bytes(original)
        app: TkoTesterApp = TkoTesterApp(ctx.settings, ctx.repo, ctx.wdir, ctx.get_task(), None)
        async with app.run_test(size=(120, 35)) as pilot:
            await pilot.press("enter")
            await pilot.pause()
            assert app.state.mode == SeqMode.finished
            assert app.state.is_all_right()
            assert app.current_task.info.rate == 100
            assert "1/1 testes concluídos" in str(app.query_one("#tester-status", Static).render())
            notifications: list[str] = [str(notification.message) for notification in app._notifications]
            assert any(str(history) in message for message in notifications) is (history_state == "invalid")

    asyncio.run(exercise())
    tracks = Tracker.load_from_log(str(ctx.track_folder / Tracker.log_file))
    assert len(tracks) == 2
    assert all(track.result == "100" for track in tracks)
    if history_state == "invalid":
        assert history.read_bytes() == original
        assert all(track.file_stamp_list == [] for track in tracks)
        assert "draft.py:" not in (ctx.track_folder / Tracker.log_file).read_text(encoding="utf-8")
    else:
        assert VersionsWriter().load_history(history).count == (3 if history_state == "conflict" else 1)
        assert VersionsWriter().load_history(history).current == "print(42)\n"
        assert all(track.file_stamp_list[0].startswith("src/py/draft.py:") for track in tracks)
