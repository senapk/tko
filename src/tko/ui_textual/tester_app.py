from __future__ import annotations

from collections.abc import Callable

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Footer, Static

from tko.config.app_settings import ToggleOption
from tko.config.settings import Settings
from tko.enums.diff_mode import DiffMode
from tko.game.feedback import Feedback
from tko.game.task import Task
from tko.play.gui_keys import GuiKeys
from tko.play.images import images, random_get, success_image
from tko.play.opener import Opener
from tko.repository.repository import Repository
from tko.repository.repository_watcher import RepositoryWatcher
from tko.run.diff_builder_down import DiffBuilderDown
from tko.run.diff_builder_side import DiffBuilderSide
from tko.run.solver_builder import CompileError
from tko.run.wdir import Wdir
from tko.tester.tester_executor import TesterExecutor
from tko.tester.tester_navigator import TesterNavigator
from tko.tester.tester_state import SeqMode, TesterState
from tko.tester.tester_top_bar import TesterTopBar
from tko.ui_textual.rt_adapter import to_rich_text
from tko.util.rt import RT


class TkoTesterApp(App[Callable[[], bool] | None]):
    """Textual test runner screen replacing the former terminal loop."""

    TITLE = "TKO Tester"
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    Screen { layout: vertical; background: #080808; }
    #tester-header { height: 5; border: round $primary; padding: 0 1; background: #080808; }
    #tester-status { height: 1; padding: 0 1; color: $text-muted; background: #080808; }
    #tester-output { height: 1fr; border: round $secondary; padding: 0 1; background: #080808; }
    #tester-output-content { text-wrap: nowrap; }
    Footer { background: #080808; }
    """
    BINDINGS = [
        Binding("escape", "quit", "Voltar"),
        Binding("q", "quit", "Voltar", show=False),
        Binding("left", "previous", "Caso anterior"),
        Binding("right", "next", "Próximo caso"),
        Binding("up", "scroll_up", "Subir"),
        Binding("down", "scroll_down", "Descer"),
        Binding("enter,t", "run_tests", "Testar"),
        Binding("e,backspace", "run_free", "Executar"),
        Binding(GuiKeys.pin, "toggle_lock", "Fixar"),
        Binding("tab", "change_main", "Solução"),
        Binding("d", "toggle_diff", "Diff"),
        Binding("l", "change_limit", "Limite"),
        Binding("a", "self_evaluate", "Avaliar"),
        Binding("I", "toggle_images", "Imagens"),
        Binding("v", "open_editor", "Ver Arquivos"),
    ]

    def __init__(
        self,
        settings: Settings,
        repo: Repository | None,
        wdir: Wdir,
        task: Task,
        watcher: RepositoryWatcher | None,
        opener: Opener | None = None,
        autorun: bool = False,
    ) -> None:
        super().__init__()
        self.settings = settings
        self.repo = repo
        self.wdir = wdir
        # ``App.task`` is Textual's internal asynchronous task property.
        # Keep the activity model under a distinct name.
        self.current_task = task
        self.watcher = watcher
        self.opener = opener
        self.state = TesterState(list(wdir.unit_list))
        self._autorun = autorun
        edit_mode = lambda: watcher is not None and watcher.edit_logger is not None
        audit_mode = lambda: watcher is not None and watcher.audit_logger is not None
        self.top_bar = TesterTopBar(repo, wdir, task, settings.app, edit_fn=edit_mode, audit_fn=audit_mode)
        self.executor: TesterExecutor = TesterExecutor(
            settings, repo, wdir, task, self.top_bar, on_warning=self._notify
        )
        self.navigator = TesterNavigator(settings, repo, wdir, task, self.executor, self._notify)

    def _notify(self, message: str) -> None:
        self.notify(message, severity="warning")

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(id="tester-header")
            yield Static(id="tester-status")
            with VerticalScroll(id="tester-output"):
                yield Static(id="tester-output-content")
        yield Footer()

    def on_mount(self) -> None:
        if self._autorun:
            self.action_run_tests()
        self.set_interval(0.05, self._process_running_state)
        self.refresh_view()

    def _process_running_state(self) -> None:
        if self.state.mode != SeqMode.running:
            return
        try:
            solver = self.wdir.get_solver()
            if solver.not_compiled():
                solver.prepare_exec()
            self.executor.process_one(self.state)
        except CompileError as error:
            self.notify(error.message, severity="error", timeout=8)
            self.state.mode = SeqMode.finished
        self.refresh_view()

    def _header(self) -> RT:
        width = max(20, self.query_one("#tester-header", Static).size.width - 2)
        return RT.join(
            [
                self.top_bar.build_top_line_header(self.state, width, timed=False),
                self.top_bar.build_focused_case(self.state, width),
                self.top_bar.build_unit_list(self.state, width),
            ],
            "\n",
        )

    def _status(self) -> str:
        done = len(self.state.results)
        total = len(self.wdir.unit_list)
        lock = "travado" if self.state.locked_index else "todos os casos"
        return f"{done}/{total} testes concluídos • {lock} • limite: {self.settings.app.timeout or 'sem limite'}"

    def _output_lines(self, width: int) -> list[RT]:
        if self.state.mode == SeqMode.intro:
            return [RT("Pressione Enter para testar ou e para executar a solução.", "y")]
        if self.state.is_all_right():
            return self._success_lines(width)
        solver = self.wdir.get_solver()
        if solver.has_compile_error():
            executable, _ = solver.get_executable()
            return [RT(line, "r") for line in executable.get_error_msg().plain().splitlines()]
        if not self.wdir.has_tests:
            return [RT("Nenhum teste cadastrado para esta atividade.", "y")]
        unit = self.state.get_focused_unit(self.wdir)
        if self.settings.app.diff_mode == DiffMode.DOWN:
            return DiffBuilderDown(width, unit).build_diff()
        return DiffBuilderSide(width, unit).build_diff()

    def _success_lines(self, width: int) -> list[RT]:
        """Return the legacy success art inside Textual's output panel."""
        folder = None
        if self.repo is not None:
            folder = self.repo.task_resolver.target_folder(self.current_task)
        seed = folder.name if folder is not None else self.current_task.basic.full_key
        catalog = images if self.settings.app.use_images else success_image
        artwork = random_get(catalog, seed, "static").splitlines()
        if artwork and not artwork[0]:
            artwork = artwork[1:]
        return [
            RT("Todos os testes passaram. ✓", "g*").center(width, " "),
            RT(),
            *(RT(line, "g").center(width, " ") for line in artwork),
        ]

    def refresh_view(self) -> None:
        if not self.is_mounted:
            return
        self.query_one("#tester-header", Static).update(to_rich_text(self._header()))
        self.query_one("#tester-status", Static).update(self._status())
        output = self.query_one("#tester-output", VerticalScroll)
        width = max(20, output.size.width - 2)
        content = output.query_one("#tester-output-content", Static)
        content.update(Text("\n").join(to_rich_text(line) for line in self._output_lines(width)))

    def action_previous(self) -> None:
        self.navigator.go_left(self.state)
        self.refresh_view()

    def action_next(self) -> None:
        self.navigator.go_right(self.state)
        self.refresh_view()

    def action_scroll_up(self) -> None:
        self.query_one("#tester-output", VerticalScroll).scroll_up()

    def action_scroll_down(self) -> None:
        self.query_one("#tester-output", VerticalScroll).scroll_down()

    def action_run_tests(self) -> None:
        self.executor.run_test_mode(self.state)
        self.refresh_view()

    def action_run_free(self) -> None:
        callback = self.executor.run_exec_mode(self.state)
        self.exit(result=callback)

    def action_toggle_lock(self) -> None:
        self.navigator.lock_unit(self.state)
        state = "ligado" if self.state.locked_index else "desligado"
        self.notify(f"Travamento {state}.")
        self.refresh_view()

    def action_change_main(self) -> None:
        self.navigator.change_main(self.state)
        self.refresh_view()

    def action_toggle_diff(self) -> None:
        self.settings.app.toggle_diff()
        self.settings.save_settings()
        self.notify(f"Modo de diff: {self.settings.app.diff_mode.value}")
        self.refresh_view()

    def action_change_limit(self) -> None:
        self.navigator.change_limit(self.state)
        self.notify(f"Limite: {self.settings.app.timeout or 'sem limite'}")
        self.refresh_view()

    def action_self_evaluate(self) -> None:
        repo = self.repo
        if repo is None:
            self.notify("Não há repositório para registrar a autoavaliação.", severity="warning")
            return
        from tko.ui_textual.dialogs import GradeDialog

        feedback = Feedback(repo, self.current_task)
        self.push_screen(
            GradeDialog(self.current_task, feedback, self.settings.app.ui_language == "pt-BR"),
            lambda result: self._save_self_evaluation(feedback, result),
        )

    def _save_self_evaluation(self, feedback: Feedback, result: object) -> None:
        if result is None:
            return
        from tko.logger.log_item_self import LogItemSelf
        from tko.ui_textual.dialogs import GradeResult

        if not isinstance(result, GradeResult):
            return
        try:
            feedback.save_fields(result.fields)
        except (OSError, ValueError) as error:
            self.notify(str(error), severity="error", timeout=8)
            return
        if not self.current_task.config.is_automated:
            self.current_task.info.rate = result.rate
        self.current_task.info.study = result.study
        self.current_task.info.boss = result.boss
        self.current_task.info.feedback = True
        repo = self.repo
        if repo is None:
            return
        repo.logger.store(LogItemSelf().set_task(self.current_task))
        self.notify("Autoavaliação registrada.")
        self.refresh_view()

    def action_toggle_images(self) -> None:
        self.settings.app.toggle(ToggleOption.IMAGES)
        self.settings.save_settings()
        self.notify("Imagens ativadas." if self.settings.app.use_images else "Imagens desativadas.")

    def action_open_editor(self) -> None:
        if self.opener is None:
            self.notify("Nenhum editor configurado.", severity="warning")
            return
        with self.suspend():
            self.opener.open_files()

    async def action_quit(self) -> None:
        self.exit()
