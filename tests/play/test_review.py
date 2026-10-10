"""Browsing a class keeps one comparison context across student repositories."""

from __future__ import annotations

import asyncio
import tomllib
from collections.abc import Callable
from pathlib import Path

from pytest import MonkeyPatch
from textual.widgets import Static

from tko.config.settings import Settings
from tko.game.quest import Quest
from tko.game.task import Task
from tko.play.review import ReviewSession, student_repositories
from tko.play.review_context import ReviewContext, ReviewLocation, ReviewNavigation, ReviewTarget
from tko.play.review_overview import ReviewOverviewService
from tko.repository.repository import Repository
from tko.ui_textual.app import TaskTreeView, TkoApp


def _student(parent: Path, name: str) -> Path:
    child: Path = parent / name
    config: Path = child / ".tko"
    config.mkdir(parents=True)
    (config / "repository.toml").write_text("[profile]\n", encoding="utf-8")
    return child


def _repository(folder: Path, settings: Settings, task_key: str) -> tuple[Repository, Quest, Task]:
    repo: Repository = Repository(folder, settings.rs, None, recursive_search=False)
    quest: Quest = Quest("Quest", "quest")
    quest.basic.source_name = "course"
    task: Task = Task()
    task.basic.source_name = "course"
    task.basic.key = task_key
    task.basic.title = task_key
    task.quest_key = quest.basic.full_key
    quest.add_task(task)
    repo.game.quests = {quest.basic.full_key: quest}
    repo.game.ordered_quests = [quest.basic.full_key]
    repo.game.tasks = {task.basic.full_key: task}
    repo.flags.task_view_mode.set_view_all()
    return repo, quest, task


def test_discovery_uses_only_direct_student_repositories_in_name_order(tmp_path: Path) -> None:
    second: Path = _student(tmp_path, "Bob")
    first: Path = _student(tmp_path, "alice")
    (tmp_path / "notes").mkdir()
    nested: Path = tmp_path / "group"
    _student(nested, "nested")
    (tmp_path / "shortcut").symlink_to(first, target_is_directory=True)

    assert student_repositories(tmp_path) == [first, second]


def test_review_session_moves_in_both_directions_and_restores_cwd(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    for name in ("alice", "bob", "carol"):
        _student(tmp_path, name)
    session: ReviewSession = ReviewSession(Settings(tmp_path / "settings"), tmp_path)
    visits: list[int] = []
    movements: list[ReviewNavigation | None] = [
        ReviewNavigation(1), ReviewNavigation(1), ReviewNavigation(-1), None,
    ]
    original: Path = Path.cwd()

    def visit(index: int) -> ReviewNavigation | None:
        visits.append(index)
        return movements[len(visits) - 1]

    monkeypatch.setattr(session, "_visit", visit)
    session.run()

    assert visits == [0, 1, 2, 1]
    assert Path.cwd() == original


def test_review_can_jump_to_student_selected_in_overview(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    for name in ("alice", "bob", "carol"):
        _student(tmp_path, name)
    session: ReviewSession = ReviewSession(Settings(tmp_path / "settings"), tmp_path)
    visits: list[int] = []

    def visit(index: int) -> ReviewTarget | None:
        visits.append(index)
        return ReviewTarget(2) if index == 0 else None

    monkeypatch.setattr(session, "_visit", visit)
    session.run()

    assert visits == [0, 2]


def test_review_migrates_legacy_student_on_next(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    first: Path = _student(tmp_path, "alice")
    student: Path = _student(tmp_path, "bob")
    (student / ".tko/repository.toml").write_text(
        'version = "0.2"\nsandbox_name = "course"\nsandbox_index = "README.md"\n'
        'selected = "course@old"\n', encoding="utf-8",
    )
    (student / "README.md").write_text(
        "- [ ] `@old` [Task](plan/task/README.md)\n", encoding="utf-8",
    )
    session: ReviewSession = ReviewSession(Settings(tmp_path / "settings"), tmp_path)
    opened: list[Path] = []
    original: Path = Path.cwd()

    def open_repo(repo: Repository, _index: int) -> ReviewNavigation | None:
        opened.append(repo.root_dir)
        return ReviewNavigation(1) if repo.root_dir == first else None

    monkeypatch.setattr(session, "_open_repo", open_repo)
    session.run()

    assert opened == [first, student]
    assert Path.cwd() == original
    config: dict[str, object] = tomllib.loads((student / ".tko/repository.toml").read_text(encoding="utf-8"))
    assert config["state"] == {"selected": "course@plan/task"}
    assert (student / ".tko/task-format.json").is_file()


def test_review_skips_student_when_migration_needs_recovery(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    first: Path = _student(tmp_path, "alice")
    pending: Path = first / ".tko/migration-pending.json"
    pending.write_text("{}\n", encoding="utf-8")
    second: Path = _student(tmp_path, "bob")
    session: ReviewSession = ReviewSession(Settings(tmp_path / "settings"), tmp_path)
    opened: list[Path] = []
    original: Path = Path.cwd()

    def open_repo(repo: Repository, _index: int) -> None:
        opened.append(repo.root_dir)

    monkeypatch.setattr(session, "_open_repo", open_repo)
    session.run()

    assert opened == [second]
    assert pending.read_text(encoding="utf-8") == "{}\n"
    assert Path.cwd() == original


def test_review_keeps_task_expansion_and_panel_when_switching(tmp_path: Path) -> None:
    settings: Settings = Settings(tmp_path)
    folder: Path = tmp_path / "alice"
    folder.mkdir()
    repo, quest, task = _repository(folder, settings, "target")
    context: ReviewContext = ReviewContext(
        selected_key=task.basic.full_key,
        expanded={quest.basic.full_key},
        view_mode="all",
        panel_mode="logs",
        initialized=True,
    )

    async def exercise() -> None:
        app: TkoApp = TkoApp(settings, repo, None, review_context=context, review_location=ReviewLocation("alice", 0, 2))
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.model.state.selected == task.basic.full_key
            assert quest.basic.full_key in app.model.state.expanded
            assert repo.flags.panel.is_logs()
            assert "alice (1/2)" in str(app.query_one("#review-header", Static).content)
            await pilot.press("N")
            assert app.return_value is None
            await pilot.press("n")
        assert app.return_value == ReviewNavigation(1)
        assert context.selected_key == task.basic.full_key
        assert context.expanded == {quest.basic.full_key}
        assert context.panel_mode == "logs"

    asyncio.run(exercise())


def test_uppercase_n_returns_to_previous_student(tmp_path: Path) -> None:
    settings: Settings = Settings(tmp_path)
    folder: Path = tmp_path / "bob"
    folder.mkdir()
    repo, _quest, _task = _repository(folder, settings, "target")

    async def exercise() -> None:
        app: TkoApp = TkoApp(
            settings, repo, None,
            review_context=ReviewContext(), review_location=ReviewLocation("bob", 1, 2),
        )
        async with app.run_test() as pilot:
            await pilot.press("N")
        assert app.return_value == ReviewNavigation(-1)

    asyncio.run(exercise())


def test_next_student_renders_task_title_after_layout(tmp_path: Path) -> None:
    settings: Settings = Settings(tmp_path)
    context: ReviewContext = ReviewContext(
        expanded={"course@quest"}, view_mode="all", initialized=True,
    )

    async def exercise() -> None:
        for index, name in enumerate(("alice", "bob")):
            folder: Path = tmp_path / name
            folder.mkdir()
            repo, _quest, task = _repository(folder, settings, "target")
            task.basic.title = "Nome visível da atividade após a troca"
            app: TkoApp = TkoApp(
                settings, repo, None, review_context=context,
                review_location=ReviewLocation(name, index, 2),
            )
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                tree: TaskTreeView = app.query_one(TaskTreeView)
                assert tree.size.width > 30
                label: str = str(tree._node_by_key[task.basic.full_key].label)
                assert "Nome visível" in label
                if index == 0:
                    await pilot.press("n")

    asyncio.run(exercise())


def test_missing_task_stays_comparison_target_until_user_selects_another(tmp_path: Path) -> None:
    settings: Settings = Settings(tmp_path)
    folder: Path = tmp_path / "bob"
    folder.mkdir()
    repo, quest, _task = _repository(folder, settings, "other")
    context: ReviewContext = ReviewContext(
        selected_key="course@target", expanded={quest.basic.full_key},
        view_mode="all", panel_mode="preview", initialized=True,
    )

    async def exercise() -> None:
        app: TkoApp = TkoApp(settings, repo, None, review_context=context, review_location=ReviewLocation("bob", 1, 3))
        async with app.run_test() as pilot:
            await pilot.pause()
            assert "tarefa ausente: course@target" in str(app.query_one("#review-header", Static).content)
            await pilot.press("n")
        assert context.selected_key == "course@target"

        next_folder: Path = tmp_path / "carol"
        next_folder.mkdir()
        next_repo, _next_quest, target = _repository(next_folder, settings, "target")
        next_app: TkoApp = TkoApp(
            settings, next_repo, None, review_context=context,
            review_location=ReviewLocation("carol", 2, 3),
        )
        async with next_app.run_test() as pilot:
            await pilot.pause()
            assert next_app.model.state.selected == target.basic.full_key
            assert "tarefa ausente" not in str(next_app.query_one("#review-header", Static).content)

    asyncio.run(exercise())


def test_review_temporarily_shows_unpinned_target_without_changing_filter(tmp_path: Path) -> None:
    settings: Settings = Settings(tmp_path)
    folder: Path = tmp_path / "alice"
    folder.mkdir()
    repo, quest, task = _repository(folder, settings, "target")
    context: ReviewContext = ReviewContext(
        selected_key=task.basic.full_key, expanded={quest.basic.full_key},
        view_mode="pinned", panel_mode="preview", initialized=True,
    )

    async def exercise() -> None:
        app: TkoApp = TkoApp(settings, repo, None, review_context=context, review_location=ReviewLocation("alice", 0, 2))
        async with app.run_test() as pilot:
            await pilot.pause()
            assert repo.flags.task_view_mode.is_all()
            assert app.model.state.selected == task.basic.full_key
            await pilot.press("n")
        assert context.view_mode == "pinned"

    asyncio.run(exercise())


def test_selecting_another_task_replaces_missing_comparison_target(tmp_path: Path) -> None:
    settings: Settings = Settings(tmp_path)
    folder: Path = tmp_path / "bob"
    folder.mkdir()
    repo, quest, task = _repository(folder, settings, "other")
    context: ReviewContext = ReviewContext(
        selected_key="course@missing", expanded={quest.basic.full_key},
        view_mode="all", panel_mode="preview", initialized=True,
    )

    async def exercise() -> None:
        app: TkoApp = TkoApp(settings, repo, None, review_context=context, review_location=ReviewLocation("bob", 1, 3))
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("down")
            assert app.model.state.selected == task.basic.full_key
            assert "tarefa ausente" not in str(app.query_one("#review-header", Static).content)
            await pilot.press("n")
        assert context.selected_key == task.basic.full_key

    asyncio.run(exercise())


def test_review_runs_normal_actions_and_stops_watcher(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    settings: Settings = Settings(tmp_path / "settings")
    repo, _quest, _task = _repository(tmp_path, settings, "target")
    session: ReviewSession = ReviewSession(settings, tmp_path)
    events: list[str] = []

    class Watcher:
        def __init__(self, _repo: Repository) -> None:
            events.append("watcher")

        def start_watching(
            self, log_audit: bool, audit_verbose: bool, audit_interval_seconds: int | None,
        ) -> Watcher:
            events.append("start")
            return self

        def stop_watching(self) -> Watcher:
            events.append("stop")
            return self

    class App:
        def __init__(
            self, _settings: Settings, _repo: Repository, _watcher: Watcher,
            review_context: ReviewContext, review_location: ReviewLocation,
            review_overview: ReviewOverviewService,
        ) -> None:
            events.append("app")
            assert review_context is session.context
            assert review_location.student == tmp_path.name
            assert review_overview is session.overview

        def run(self) -> Callable[[], None] | ReviewNavigation:
            if events.count("app") == 1:
                return lambda: events.append("normal action")
            return ReviewNavigation(1)

    monkeypatch.setattr("tko.play.review.LanguageSetter.check_prog_lang_in_text_mode", lambda _settings, _repo: None)
    monkeypatch.setattr("tko.play.review.RepositoryWatcher", Watcher)
    monkeypatch.setattr("tko.play.review.TkoApp", App)

    assert session._open_repo(repo, 0) == ReviewNavigation(1)
    assert events == ["watcher", "start", "app", "normal action", "app", "stop"]
