from __future__ import annotations

from tko.ui_textual.palette import DARK, LIGHT, THEMES, make_theme

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Protocol

from rich.text import Text
from textual import events, on
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingsMap
from textual.containers import Grid, Horizontal, ItemGrid, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Input, Label, Static, Tree
from textual.widgets._tree import NodeID, TreeNode

from tko.config.flags import PanelMode
from tko.config.app_settings import ToggleOption
from tko.config.settings import Settings
from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.tree_item import IsTreeItem
from tko.play.daily_graph import DailyGraph
from tko.play.gui_keys import GuiKeys
from tko.play.preview_service import PreviewService
from tko.play.search import Search
from tko.play.task_action import TaskAction
from tko.play_gui.gui_graph_panel import GuiGraphPanel
from tko.play_gui.gui_skills_bar import GuiSkillsBar
from tko.play_tree.task_formatter import TaskFormatter
from tko.play_tree.task_tree import TaskTree
from tko.repository.repository import Repository
from tko.repository.repository_watcher import RepositoryWatcher
from tko.ui_textual.preview_markdown import render_preview_markdown
from tko.ui_textual.rt_adapter import to_rich_text
from tko.util.rt import RT


class TreeViewState(Protocol):
    """Subset of tree state required by the Textual tree widget."""

    selected: str
    expanded: set[str]


class TreeViewTaskFormatter(Protocol):
    """Task materialization query required for mouse activation."""

    def is_downloaded_for_lang(self, task: Task) -> bool: ...


class TaskTreeViewModel(Protocol):
    """Presentation-model contract consumed by :class:`TaskTreeView`."""

    @property
    def state(self) -> TreeViewState: ...

    @property
    def task_formatter(self) -> TreeViewTaskFormatter: ...

    def update(self) -> None: ...

    def get_rendered_items(self) -> Iterable[tuple[RT, IsTreeItem]]: ...

    def move_left(self) -> None: ...

    def move_right(self) -> None: ...


class HelpScreen(ModalScreen[None]):
    """Native modal screen for the keyboard-reference view."""

    DEFAULT_CSS = """
    HelpScreen { align: center middle; }
    #help-dialog { width: 76; height: auto; max-height: 80%; padding: 1 2; border: round $accent; background: $surface; }
    """

    def __init__(self, portuguese: bool = True) -> None:
        super().__init__()
        self.portuguese = portuguese

    def compose(self) -> ComposeResult:
        title = "Atalhos do TKO" if self.portuguese else "TKO shortcuts"
        content = (
            "↑/↓ navegar  •  ←/→ expandir/contrair  •  Enter abrir/executar\n"
            "/ buscar  •  f fixar  •  b baixar  •  1/2 tarefas  •  3/4/5/6 painel\n"
            "Gráfico: 4 alterna eixo X • PgUp execuções • PgDn tempo (min)\n"
            "Tab alternar painel  •  [/] expandir/compactar tudo  •  R recarregar  •  q sair\n\n"
            "Pressione Esc para fechar."
            if self.portuguese
            else "↑/↓ navigate  •  ←/→ expand/collapse  •  Enter open/run\n"
            "/ search  •  f pin  •  b download  •  1/2 tasks  •  3/4/5/6 panel\n"
            "Graph: 4 switches X axis • PgUp executions • PgDn time (min)\n"
            "Tab switch panel  •  [/] expand/collapse all  •  R reload  •  q quit\n\n"
            "Press Esc to close."
        )
        yield Vertical(
            Label(title, classes="title"),
            Static(content, markup=False),
            id="help-dialog",
        )

    BINDINGS = [Binding("escape,question_mark", "dismiss", "Fechar", show=False)]

    async def action_dismiss(self, result: None = None) -> None:
        await self.dismiss(result)


class TaskTreeView(Tree[IsTreeItem]):
    """Tree widget whose nodes mirror the existing TaskTree state."""

    BINDINGS = [
        Binding("left", "legacy_left", "Contrair", show=False),
        Binding("right", "legacy_right", "Expandir", show=False),
    ]

    def __init__(self, model: TaskTreeViewModel) -> None:
        super().__init__("TKO", id="task-tree")
        self.model = model
        self.task_formatter = model.task_formatter
        self.show_root = False
        self.guide_depth = 2
        self._node_by_key: dict[str, TreeNode[IsTreeItem]] = {}

    def rebuild(self) -> None:
        self.model.update()
        self.clear()
        self._node_by_key.clear()
        quest_nodes: dict[str, TreeNode[IsTreeItem]] = {}
        for sentence, item in self.model.get_rendered_items():
            label = to_rich_text(sentence, THEMES.get(self.app.theme, DARK))
            if isinstance(item, Quest):
                expanded = item.basic.full_key in self.model.state.expanded
                node = self.root.add(label, data=item, expand=expanded, allow_expand=True)
                quest_nodes[item.basic.full_key] = node
                self._node_by_key[item.basic.full_key] = node
            elif isinstance(item, Task):
                parent = quest_nodes.get(item.quest_key, self.root)
                node = parent.add_leaf(label, data=item)
                self._node_by_key[item.basic.full_key] = node
        selected_key = self.model.state.selected
        if self.is_mounted:
            # Nodes receive their screen line during the next layout pass, so
            # restore the cursor after Textual has refreshed this tree.
            self.call_after_refresh(self._restore_cursor, selected_key)

    def _restore_cursor(self, key: str) -> None:
        selected = self._node_by_key.get(key)
        if selected is not None:
            self.move_cursor(selected)  # type: ignore[arg-type]

    def is_current_node(self, node: TreeNode[IsTreeItem]) -> bool:
        """Return whether an event belongs to the current rebuilt tree."""
        item = node.data
        return item is not None and self._node_by_key.get(item.basic.full_key) is node

    def action_legacy_left(self) -> None:
        self.model.move_left()
        self.rebuild()

    def action_legacy_right(self) -> None:
        self.model.move_right()
        self.rebuild()

    @on(events.Click)
    def _handle_mouse_click(self, event: events.Click) -> None:
        """Use the mouse for tree navigation, never for task activation."""
        # Textual dispatches both this override and Tree._on_click through the
        # MRO. Without preventing its default action, Tree subsequently emits
        # NodeSelected and activates the task (or toggles a quest a second
        # time).
        event.prevent_default()
        meta = event.style.meta
        line = meta.get("line")
        node = self.get_node_at_line(line) if isinstance(line, int) else None
        if node is None:
            # Labels receive a node id from Textual; guides receive a line.
            node_id = meta.get("node")
            if isinstance(node_id, int):
                node = self._tree_nodes.get(NodeID(node_id))
        if node is None:
            node = self.get_node_at_line(event.y + self.scroll_offset.y)
        if node is None or node.data is None:
            return

        # Mouse interaction is deliberately selection-only. Expansion and
        # activation remain explicit keyboard operations, except for an
        # explicit double-click on a quest.
        self.cursor_line = node._line
        self.model.state.selected = node.data.basic.full_key
        self.post_message(Tree.NodeHighlighted(node))
        if event.chain >= 2 and isinstance(node.data, Quest):
            self.toggle_fold(node)
        elif event.chain >= 2 and isinstance(node.data, Task):
            if self.task_formatter.is_downloaded_for_lang(node.data):
                # Reuse the exact NodeSelected route used by Enter. The app
                # then decides whether this materialized task starts Tester.
                self.post_message(Tree.NodeSelected(node))
            else:
                self.notify(
                    "Aperte Enter ou clique b para baixar a tarefa.",
                    severity="information",
                )

    def toggle_fold(self, node: TreeNode[IsTreeItem]) -> None:
        """Toggle a quest and rebuild from the authoritative tree state."""
        quest = node.data
        if not isinstance(quest, Quest):
            return
        key = quest.basic.full_key
        if key in self.model.state.expanded:
            self.model.state.expanded.discard(key)
        else:
            self.model.state.expanded.add(key)
        self.rebuild()


class TkoApp(App[Callable[[], None] | None]):
    """The Textual replacement for the repository browser in ``tko open``."""

    TITLE = "TKO"
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    Screen { layout: vertical; background: $background; }
    .panel-header .top-action { width: 1fr; min-width: 0; height: 1; padding: 0 1; border: none; background: $primary; color: $background; }
    .panel-header .top-action:hover { background: $primary; }
    .panel-header .top-action.active { background: $accent; color: $text; text-style: bold; }
    #body { height: 1fr; background: $background; }
    .play-frame { height: 100%; border: round $border; background: $background; }
    .play-frame:focus-within { border: round $primary; }
    #task-frame { width: 45%; min-width: 28; }
    #info-frame { width: 55%; min-width: 30; }
    .panel-header { height: auto; grid-rows: 1; background: $background; }
    #graph-footer { grid-size: 2; grid-columns: 1fr 1fr; display: none; }
    #graph-footer .top-action { padding: 0; }
    #task-tree { width: 100%; height: 1fr; border: none; background: $background; }
    #side-panel { width: 100%; height: 1fr; border: none; padding: 0 1; background: $background; }
    #side-content { width: auto; min-width: 100%; height: auto; text-wrap: nowrap; background: $background; }
    #side-content.preview { width: 100%; text-wrap: wrap; }
    Footer { background: $background; }
    #search { display: none; margin: 0 1; }
    #search.visible { display: block; }
    .title { text-style: bold; }
    """

    BINDINGS = [
        Binding("q", "quit", "Sair", show=False),
        Binding("escape", "escape", "Sair"),
        Binding("slash", "search", "Buscar"),
        Binding("tab,shift+tab", "toggle_panel_focus", "Alternar painel", show=False, priority=True),
        Binding(GuiKeys.all_tasks, "show_all", "Todas", show=False),
        Binding(GuiKeys.inbox, "show_pinned", "Fixadas", show=False),
        Binding(GuiKeys.panel_preview, "show_preview", "Prévia", show=False),
        Binding(GuiKeys.panel_graph, "show_graph", "Gráfico", show=False),
        Binding(GuiKeys.panel_logs, "show_logs", "Logs", show=False),
        Binding(GuiKeys.panel_skills, "show_skills", "Trilhas", show=False),
        Binding(GuiKeys.self_evaluate, "self_evaluate", "Avaliar"),
        Binding(GuiKeys.down_task, "download", "Baixar"),
        Binding(GuiKeys.pin, "toggle_pin", "Fixar"),
        Binding("delete", "delete_task", "Excluir"),
        Binding("shift+delete", "delete_task_without_confirmation", "Excluir sem confirmação", show=False),
        Binding(GuiKeys.expand_all, "expand_all", "Expandir", show=False),
        Binding(GuiKeys.collapse_all, "collapse_all", "Compactar", show=False),
        Binding(GuiKeys.reload_game, "reload", "Recarregar"),
        Binding(GuiKeys.show_duration, "toggle_time", "Tempo"),
        Binding(GuiKeys.set_lang_drafts, "choose_language", "Linguagem"),
        Binding(GuiKeys.palette, "palette", "Ações"),
        Binding("less_than_sign", "panel_smaller", "\u00a0", key_display="<", tooltip="Diminuir painel"),
        Binding("greater_than_sign", "panel_larger", "\u00a0", key_display=">", tooltip="Aumentar painel"),
        Binding("pageup", "scroll_logs_up", "Logs acima", show=False, priority=True),
        Binding("pagedown", "scroll_logs_down", "Logs abaixo", show=False, priority=True),
        Binding("question_mark", "help", "Ajuda"),
        Binding(GuiKeys.colors, "toggle_theme", "Cores"),
    ]

    def __init__(self, settings: Settings, repo: Repository, watcher: RepositoryWatcher | None, need_update: bool = False) -> None:
        super().__init__()
        self.register_theme(make_theme(DARK))
        self.register_theme(make_theme(LIGHT))
        self.settings = settings
        self.theme = settings.app.theme if settings.app.theme in THEMES else DARK.name
        self._bindings = BindingsMap(self._localized_bindings())
        self.repo = repo
        self.watcher = watcher
        self.need_update = need_update
        self.model = TaskTree(settings, repo)
        # TreeRenderer keeps task and quest text within the available tree
        # content width. The callback is evaluated only while rendering, after
        # the widget has a layout size.
        self.model.layout.get_tree_size_fn = self._tree_content_width
        self.task_formatter = TaskFormatter(settings, repo)
        self.preview: PreviewService = PreviewService(repo.task_resolver)
        self._panel_context: tuple[str, str | None] | None = None
        self.search = Search(self.model)
        self.graph = GuiGraphPanel(settings, repo, repo.flags)
        self.skills = GuiSkillsBar(repo.game, settings.colors, repo.flags, lambda: self._selected_source())

    def _localized_bindings(self) -> list[Binding]:
        return [
            Binding("q", "quit", self._t("Sair", "Quit"), show=False),
            Binding("escape", "escape", self._t("Sair", "Quit")),
            Binding("slash", "search", self._t("Buscar", "Search")),
            Binding("tab,shift+tab", "toggle_panel_focus", self._t("Alternar painel", "Switch panel"), show=False, priority=True),
            Binding(GuiKeys.all_tasks, "show_all", self._t("Todas", "All"), show=False),
            Binding(GuiKeys.inbox, "show_pinned", self._t("Fixadas", "Pinned"), show=False),
            Binding(GuiKeys.panel_preview, "show_preview", self._t("Prévia", "Preview"), show=False),
            Binding(GuiKeys.panel_graph, "show_graph", self._t("Gráfico", "Graph"), show=False),
            Binding(GuiKeys.panel_logs, "show_logs", "Logs", show=False),
            Binding(GuiKeys.panel_skills, "show_skills", self._t("Trilhas", "Skills"), show=False),
            Binding(GuiKeys.self_evaluate, "self_evaluate", self._t("Avaliar", "Evaluate")),
            Binding(GuiKeys.down_task, "download", self._t("Baixar", "Download")),
            Binding(GuiKeys.pin, "toggle_pin", self._t("Fixar", "Pin")),
            Binding("delete", "delete_task", self._t("Excluir", "Delete")),
            Binding("shift+delete", "delete_task_without_confirmation", self._t("Excluir sem confirmação", "Delete without confirmation"), show=False),
            Binding(GuiKeys.expand_all, "expand_all", self._t("Expandir", "Expand"), show=False),
            Binding(GuiKeys.collapse_all, "collapse_all", self._t("Compactar", "Collapse"), show=False),
            Binding("I", "toggle_ui_language", self._t("Idiomas", "Interface")),
            Binding(GuiKeys.set_lang_drafts, "choose_language", self._t("Linguagem", "Programming")),
            Binding(GuiKeys.palette, "palette", self._t("Paleta", "Palette")),
            Binding(GuiKeys.reload_game, "reload", self._t("Recarregar", "Reload")),
            Binding(GuiKeys.show_duration, "toggle_time", self._t("Tempo", "Time")),
            Binding("less_than_sign", "panel_smaller", "\u00a0", key_display="<", tooltip=self._t("Diminuir painel", "Shrink panel")),
            Binding("greater_than_sign", "panel_larger", "\u00a0", key_display=">", tooltip=self._t("Aumentar painel", "Grow panel")),
            Binding("pageup", "scroll_logs_up", self._t("Rolar painel acima", "Scroll panel up"), show=False, priority=True),
            Binding("pagedown", "scroll_logs_down", self._t("Rolar painel abaixo", "Scroll panel down"), show=False, priority=True),
            Binding("question_mark", "help", self._t("Ajuda", "Help")),
            Binding(GuiKeys.colors, "toggle_theme", self._t("Cores", "Colors")),
        ]

    def _t(self, portuguese: str, english: str) -> str:
        return portuguese if self.settings.app.ui_language == "pt-BR" else english

    def _refresh_language(self) -> None:
        self._bindings = BindingsMap(self._localized_bindings())
        self.screen.refresh_bindings()
        self.query_one("#search", Input).placeholder = self._t("Buscar tarefas…", "Search tasks…")
        self.refresh_view()

    def compose(self) -> ComposeResult:
        yield Input(placeholder=self._t("Buscar tarefas…", "Search tasks…"), id="search")
        with Horizontal(id="body"):
            with Vertical(id="task-frame", classes="play-frame"):
                with ItemGrid(id="task-header", classes="panel-header", min_column_width=14, regular=True):
                    yield Button(id="top-all", classes="top-action")
                    yield Button(id="top-pinned", classes="top-action")
                yield TaskTreeView(self.model)
            with Vertical(id="info-frame", classes="play-frame"):
                with ItemGrid(id="info-header", classes="panel-header", min_column_width=14, regular=True):
                    yield Button(id="top-preview", classes="top-action")
                    yield Button(id="top-graph", classes="top-action")
                    yield Button(id="top-logs", classes="top-action")
                    yield Button(id="top-skills", classes="top-action")
                with ScrollableContainer(id="side-panel"):
                    yield Static(id="side-content")
                with Grid(id="graph-footer", classes="panel-header"):
                    yield Button(id="graph-executions", classes="top-action")
                    yield Button(id="graph-time", classes="top-action")
        yield Footer()

    def on_mount(self) -> None:
        if self.watcher is not None:
            self.watcher.set_audit_notification_callback(self._notify_audit)
        self._apply_panel_size()
        self.refresh_view()
        self.call_after_refresh(self.refresh_view)
        self.query_one(TaskTreeView).focus()
        if self.need_update:
            from tko.config.check_version import CheckVersion

            command: str = CheckVersion.update_command()
            self.notify(
                self._t(
                    f"Nova versão do TKO disponível. Atualize com: {command}",
                    f"A new TKO version is available. Update with: {command}",
                ),
                severity="information",
                timeout=10,
            )

    def on_unmount(self) -> None:
        if self.watcher is not None:
            self.watcher.set_audit_notification_callback(None)

    def _notify_audit(self, message: str) -> None:
        self.call_from_thread(self.notify, message, severity="information")

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "toggle_panel_focus":
            return not isinstance(self.screen, ModalScreen)
        return super().check_action(action, parameters)

    def action_toggle_panel_focus(self) -> None:
        tree: TaskTreeView = self.query_one(TaskTreeView)
        panel: ScrollableContainer = self.query_one("#side-panel", ScrollableContainer)
        if self.focused is not None and self.query_one("#task-frame", Vertical) in self.focused.ancestors:
            panel.focus()
        else:
            tree.focus()

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted[IsTreeItem]) -> None:
        if event.node.data is not None:
            self.model.state.selected = event.node.data.basic.full_key
            self.refresh_panel()

    def on_tree_node_expanded(self, event: Tree.NodeExpanded[IsTreeItem]) -> None:
        tree = self.query_one(TaskTreeView)
        if tree.is_current_node(event.node) and isinstance(event.node.data, Quest):
            self.model.state.expanded.add(event.node.data.basic.full_key)

    def on_tree_node_collapsed(self, event: Tree.NodeCollapsed[IsTreeItem]) -> None:
        tree = self.query_one(TaskTreeView)
        if tree.is_current_node(event.node) and isinstance(event.node.data, Quest):
            self.model.state.expanded.discard(event.node.data.basic.full_key)

    def on_tree_node_selected(self, event: Tree.NodeSelected[IsTreeItem]) -> None:
        if event.node.data is not None:
            self.action_activate()

    def on_input_changed(self, event: Input.Changed) -> None:
        # Clearing the widget while hiding it emits Input.Changed. Once the
        # search session has finished, that empty value must not select the
        # first unfiltered entry again.
        if event.input.id != "search" or not self.search.search_mode:
            return
        self.model.state.search = event.value.lower()
        self.search.update_index()
        self.refresh_tree()

    def on_key(self, event: events.Key) -> None:
        """Navigate search results while the search input owns keyboard focus."""
        search_input = self.query_one("#search", Input)
        if (
            not self.search.search_mode
            or self.focused is not search_input
            or event.key not in {"up", "down"}
        ):
            return

        event.stop()
        if event.key == "up":
            self.model.move_up()
        else:
            self.model.move_down()
        self.refresh_tree()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search":
            self.search.finish_search()
            self._hide_search()
            self.refresh_view()

    def on_resize(self) -> None:
        if self.is_mounted:
            self.refresh_view()

    def _tree_content_width(self) -> int:
        """Width available to a rendered tree row inside its enclosing frame."""
        tree = self.query_one("#task-tree", TaskTreeView)
        return max(30, tree.size.width)

    def _selected_source(self) -> str:
        try:
            return self.model.get_selected_throw().basic.source_name
        except IndexError:
            return ""

    def _selected_item(self) -> IsTreeItem | None:
        try:
            return self.model.get_selected_throw()
        except IndexError:
            return None

    def _refresh_panel_headers(self) -> None:
        actions = [
            ("top-all", GuiKeys.all_tasks, self._t("Todas", "All"), not self.repo.flags.task_view_mode.is_pinned()),
            ("top-pinned", GuiKeys.inbox, self._t("Fixadas", "Pinned"), self.repo.flags.task_view_mode.is_pinned()),
            ("top-preview", GuiKeys.panel_preview, self._t("Prévia", "Preview"), self.repo.flags.panel.is_preview()),
            ("top-graph", GuiKeys.panel_graph, self._t("Gráfico", "Graph"), self.repo.flags.panel.is_graph()),
            ("top-logs", GuiKeys.panel_logs, "Logs", self.repo.flags.panel.is_logs()),
            ("top-skills", GuiKeys.panel_skills, self._t("Trilhas", "Skills"), self.repo.flags.panel.is_skills()),
        ]
        for identifier, key, label, active in actions:
            button = self.query_one(f"#{identifier}", Button)
            button.label = Text(f"{label} [{key}]")
            button.set_class(active, "active")

    def refresh_tree(self) -> None:
        self.query_one(TaskTreeView).rebuild()
        self.refresh_panel()

    def refresh_view(self) -> None:
        self._refresh_panel_headers()
        self.refresh_tree()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "top-all": self.action_show_all,
            "top-pinned": self.action_show_pinned,
            "top-preview": self.action_show_preview,
            "top-graph": self.action_show_graph,
            "top-logs": self.action_show_logs,
            "top-skills": self.action_show_skills,
            "graph-time": self.action_graph_time,
            "graph-executions": self.action_graph_executions,
        }
        button_id = event.button.id
        action = actions.get(button_id) if button_id is not None else None
        if action is not None:
            action()

    def refresh_panel(self) -> None:
        panel = self.query_one("#side-panel", ScrollableContainer)
        width = max(12, panel.size.width - 2)
        item = self._selected_item()
        self._refresh_graph_footer(item)
        context: tuple[str, str | None] = (
            self.repo.flags.panel.get_value(), item.basic.full_key if item is not None else None
        )
        if context != self._panel_context:
            panel.scroll_home(animate=False)
            self._panel_context = context
        content: Static = self.query_one("#side-content", Static)
        content.set_class(self.repo.flags.panel.is_preview(), "preview")
        if self.repo.flags.panel.is_preview():
            result = self.preview.load(item if isinstance(item, Task) else None)
            if result.status == "ready":
                content.update(render_preview_markdown(result.markdown))
            else:
                messages: dict[str, tuple[str, str]] = {
                    "select": ("Selecione uma tarefa para visualizar seu README.", "Select a task to preview its README."),
                    "unavailable": ("README indisponível na fonte local.", "README unavailable in the local source."),
                    "unreadable": ("Não foi possível ler o README da fonte.", "Unable to read the source README."),
                    "empty": ("O README da fonte está vazio.", "The source README is empty."),
                }
                content.update(Text(self._t(*messages[result.status])))
            return
        lines: list[RT]
        if self.repo.flags.panel.is_skills():
            lines = self._skill_lines(width)
        elif self.repo.flags.panel.is_logs():
            if isinstance(item, Task):
                _, header, task_lines = self.graph.get_task_graph(item.basic.full_key, width, max(3, panel.size.height - 1))
                lines = header + task_lines
            elif isinstance(item, Quest):
                _, header, history_lines = self.graph.get_history(item)
                lines = header + history_lines
            else:
                lines = [RT(self._t("Selecione uma tarefa ou missão.", "Select a task or quest."))]
        else:
            lines = self._graph_lines(item, width, max(3, panel.size.height - 1))
        self.query_one("#side-content", Static).update(Text("\n").join(to_rich_text(line, THEMES[self.theme]) for line in lines))

    def action_toggle_theme(self) -> None:
        self.theme = LIGHT.name if self.theme == DARK.name else DARK.name
        self.settings.app.set_theme(self.theme)
        self.settings.save_settings()
        self.refresh_view()

    def _refresh_graph_footer(self, item: IsTreeItem | None) -> None:
        footer: Grid = self.query_one("#graph-footer", Grid)
        visible: bool = self.repo.flags.panel.is_graph()
        if footer.display != visible:
            footer.display = visible
            self.call_after_refresh(self.refresh_panel)
        time_view: bool = self.repo.flags.task_graph_mode.is_time_view()
        options: list[tuple[str, str, bool]] = [
            ("graph-executions", self._t("Gráfico Execução [PgUp]", "Execution Graph [PgUp]"), not time_view),
            ("graph-time", self._t("Gráfico Tempo [PgDown]", "Time Graph [PgDown]"), time_view),
        ]
        for identifier, label, active in options:
            button: Button = self.query_one(f"#{identifier}", Button)
            button.label = Text(label)
            button.disabled = not isinstance(item, Task)
            button.set_class(active, "active")

    def action_graph_time(self) -> None:
        self.repo.flags.task_graph_mode.set_time_view()
        self.refresh_panel()

    def action_graph_executions(self) -> None:
        self.repo.flags.task_graph_mode.set_exec_view()
        self.refresh_panel()

    def action_scroll_logs_up(self) -> None:
        if self.repo.flags.panel.is_graph():
            self.action_graph_executions()
        if self.repo.flags.panel.is_logs() or self.repo.flags.panel.is_preview():
            self.query_one("#side-panel", ScrollableContainer).scroll_page_up()

    def action_scroll_logs_down(self) -> None:
        if self.repo.flags.panel.is_graph():
            self.action_graph_time()
        if self.repo.flags.panel.is_logs() or self.repo.flags.panel.is_preview():
            self.query_one("#side-panel", ScrollableContainer).scroll_page_down()

    def _graph_lines(self, item: IsTreeItem | None, width: int, height: int) -> list[RT]:
        if isinstance(item, Task):
            # TaskGraph reserves one row for its header; DailyGraph does not.
            _, header, lines = self.graph.get_task_graph(item.basic.full_key, width, height + 1)
            return lines + [info.center(width) for info in header]
        if isinstance(item, Quest):
            header, lines = DailyGraph(self.repo.logger, width, height).get_graph()
            return lines + [info.center(width) for info in header]
        return [RT(self._t("Selecione uma tarefa ou missão.", "Select a task or quest."))]

    def _skill_lines(self, width: int) -> list[RT]:
        # GuiSkillsBar owns the formatting and bar rules. Reuse its public
        # builders while Textual owns borders, sizing and scrolling.
        from tko.game.xp_resume import XPResume

        quests = {key: quest for key, quest in self.repo.game.quests.items() if quest.basic.source_name == self._selected_source()}
        resume = XPResume(quests)
        skills = resume.get_skills_resume()
        if not skills:
            return [RT(self._t("Nenhuma trilha disponível para a seleção.", "No skills available for this selection."))]
        target = max((value.target100 for value in skills.values()), default=1) * self.skills.target_cut_factor
        lines = [self.skills.get_entry_xp(skills, skill, target, width) for skill in skills]
        total = resume.sum_xp(skills, self.skills.overload)
        grade = total.obtained / total.target100 * 10 if total.target100 else 0
        lines.append(RT(f" Nota: {grade:.1f}"))
        return lines

    def _hide_search(self) -> None:
        search = self.query_one("#search", Input)
        search.remove_class("visible")
        search.value = ""
        self.query_one(TaskTreeView).focus()

    def action_search(self) -> None:
        if not self.search.search_mode:
            self.search.toggle_search()
        search = self.query_one("#search", Input)
        search.add_class("visible")
        search.focus()

    def action_cancel_search(self) -> None:
        if self.search.search_mode:
            self.search.cancel_search()
            self._hide_search()
            self.refresh_view()

    async def action_escape(self) -> None:
        if self.search.search_mode:
            self.action_cancel_search()
            return
        await self.action_quit()

    def action_show_pinned(self) -> None:
        if not self.model.has_pinned_tasks():
            self.notify("Nenhuma tarefa fixada.", severity="warning")
            return
        self.repo.flags.task_view_mode.set_view_pinned()
        self.refresh_view()

    def action_show_all(self) -> None:
        self.repo.flags.task_view_mode.set_view_all()
        self.refresh_view()

    def _set_panel(self, value: str) -> None:
        self.repo.flags.panel.set_value(value)
        self.refresh_view()

    def action_show_graph(self) -> None:
        if self.repo.flags.panel.is_graph():
            self.repo.flags.task_graph_mode.toggle()
        self._set_panel(PanelMode.GRAPH)

    def action_show_logs(self) -> None:
        self._set_panel(PanelMode.LOGS)

    def action_show_skills(self) -> None:
        self._set_panel(PanelMode.SKILLS)

    def action_show_preview(self) -> None:
        self._set_panel(PanelMode.PREVIEW)

    def action_toggle_pin(self) -> None:
        item = self._selected_item()
        if not isinstance(item, Task):
            self.notify("Selecione uma tarefa para fixá-la.", severity="warning")
            return
        if item.basic.full_key in self.model.state.pinned:
            self.model.state.pinned.remove(item.basic.full_key)
            self.notify("Tarefa desafixada.")
        else:
            self.model.state.pinned.add(item.basic.full_key)
            self.notify("Tarefa fixada.")
        self.model.save_state()
        self.refresh_view()

    def action_download(self) -> None:
        """Materialize the selected task while preserving existing starters."""
        task = self._selected_item()
        if not isinstance(task, Task):
            self.notify(
                self._t("Selecione uma tarefa para baixar.", "Select a task to download."),
                severity="warning",
            )
            return
        self._download_task(task)

    def action_expand_all(self) -> None:
        self.model.expand_all()
        self.refresh_tree()

    def action_collapse_all(self) -> None:
        self.model.collapse_all()
        self.refresh_tree()

    def action_reload(self) -> None:
        from tko.cmds.drafts_finder_cached import DraftsFinderCached
        from tko.repository.game_coordinator import GameCoordinator

        DraftsFinderCached.reset_cache()
        try:
            GameCoordinator(self.repo).load_game()
        except FileNotFoundError as error:
            self.notify(str(error), severity="error", timeout=8)
            return
        self.model.recalculate_layout()
        self.refresh_view()
        self.notify("Repositório recarregado.")

    def action_help(self) -> None:
        self.push_screen(HelpScreen(self.settings.app.ui_language == "pt-BR"))

    def action_choose_language(self) -> None:
        from tko.repository.repository_config import RepositoryLoader
        from tko.ui_textual.dialogs import ChoiceDialog

        languages = sorted(self.settings.get_languages_settings().get_languages_with_drafts())
        if not languages:
            self.notify("Nenhuma linguagem com rascunho configurada.", severity="warning")
            return

        def save(language: str | None) -> None:
            if language is None:
                return
            self.repo.data.lang = language
            RepositoryLoader(self.repo).save()
            self.notify(f"Linguagem alterada para {language}.")
            self.refresh_view()

        self.push_screen(
            ChoiceDialog(
                self._t("Linguagem padrão dos rascunhos", "Default draft language"),
                [(language, language) for language in languages],
                self.repo.data.lang,
                self._t("↑/↓ ou clique para escolher • Enter seleciona • Esc cancela", "↑/↓ or click to choose • Enter selects • Esc cancels"),
            ),
            save,
        )

    def _apply_panel_size(self) -> None:
        panel_percent = self.settings.app.panel_size_percent
        self.query_one("#task-frame", Vertical).styles.width = f"{panel_percent}%"
        self.query_one("#info-frame", Vertical).styles.width = f"{100 - panel_percent}%"

    def action_palette(self) -> None:
        from tko.ui_textual.dialogs import CommandPalette

        commands = [
            ("download", self._t("Baixar tarefa selecionada  [b]", "Download selected task  [b]")),
            ("evaluate", self._t("Avaliar tarefa  [a]", "Evaluate task  [a]")),
            ("delete", self._t("Excluir tarefa local  [Del]", "Delete local task  [Del]")),
            ("draft", self._t("Criar rascunho  [r]", "Create draft  [r]")),
            ("language", self._t("Mudar linguagem de programação dos rascunhos  [L]", "Change draft programming language  [L]")),
            ("ui-language", self._t("Alternar idioma da interface  [I]", "Toggle interface language  [I]")),
            ("reload", self._t("Recarregar repositório  [R]", "Reload repository  [R]")),
            ("images", self._t("Alternar imagens após testes", "Toggle images after tests")),
            ("duration", self._t("Alternar tempo nas tarefas  [T]", "Toggle task time  [T]")),
            ("versions", self._t("Abrir versões da tarefa  [V]", "Open task versions  [V]")),
            ("panel-larger", self._t("Aumentar painel de tarefas  [>]", "Grow task panel  [>]")),
            ("panel-smaller", self._t("Diminuir painel de tarefas  [<]", "Shrink task panel  [<]")),
        ]
        self.push_screen(
            CommandPalette(
                commands,
                self._t("Ações e configurações", "Actions and settings"),
                self._t("↑/↓ ou clique para escolher • Enter executa • Esc fecha", "↑/↓ or click to choose • Enter runs • Esc closes"),
            ),
            self._run_palette_command,
        )

    def _run_palette_command(self, command: str | None) -> None:
        if command is None:
            return
        if command == "download":
            self.action_download()
        elif command == "evaluate":
            self._ask_self_evaluation()
        elif command == "delete":
            self._ask_delete_task()
        elif command == "draft":
            self._ask_draft_title()
        elif command == "language":
            self.action_choose_language()
        elif command == "ui-language":
            self.action_toggle_ui_language()
        elif command == "reload":
            self.action_reload()
        elif command == "images":
            self.settings.app.toggle(ToggleOption.IMAGES)
            self.settings.save_settings()
            self.notify("Imagens ativadas." if self.settings.app.use_images else "Imagens desativadas.")
        elif command == "duration":
            self.action_toggle_time()
        elif command == "versions":
            self._open_versions()
        elif command.startswith("panel-"):
            if command == "panel-larger":
                self.action_panel_larger()
            else:
                self.action_panel_smaller()

    def action_toggle_ui_language(self) -> None:
        from tko.i18n import set_language

        language = "en" if self.settings.app.ui_language == "pt-BR" else "pt-BR"
        self.settings.app.ui_language = language
        set_language(language)
        self.settings.save_settings()
        self._refresh_language()
        self.notify("Idioma alterado." if language == "pt-BR" else "Interface language changed.")

    def action_toggle_time(self) -> None:
        self.repo.flags.show_time.toggle()
        self.model.save_state()
        self.refresh_view()

    def action_delete_task(self) -> None:
        self._ask_delete_task()

    def action_delete_task_without_confirmation(self) -> None:
        self._ask_delete_task(confirm=False)

    def _resize_panel(self, amount: int) -> None:
        previous = self.settings.app.panel_size_percent
        self.settings.app.panel_size_percent = max(30, min(70, previous + amount))
        if self.settings.app.panel_size_percent == previous:
            self.notify("O painel já está no limite de tamanho.")
            return
        self.settings.save_settings()
        self._apply_panel_size()
        self.refresh_view()

    def action_panel_larger(self) -> None:
        self._resize_panel(10)

    def action_panel_smaller(self) -> None:
        self._resize_panel(-10)

    def _ask_self_evaluation(self) -> None:
        from tko.game.feedback import Feedback
        from tko.ui_textual.dialogs import GradeDialog

        task = self._selected_item()
        if not isinstance(task, Task) or not task.config.supports_self_evaluation:
            self.notify("A tarefa selecionada não permite autoavaliação.", severity="warning")
            return
        feedback = Feedback(self.repo, task)
        self.push_screen(
            GradeDialog(task, feedback, self.settings.app.ui_language == "pt-BR"),
            lambda result: self._save_self_evaluation(task, feedback, result),
        )

    def action_self_evaluate(self) -> None:
        self._ask_self_evaluation()

    def _save_self_evaluation(self, task: Task, feedback: object, result: object) -> None:
        if result is None:
            return
        from tko.game.feedback import Feedback
        from tko.ui_textual.dialogs import GradeResult

        if not isinstance(feedback, Feedback) or not isinstance(result, GradeResult):
            return
        from tko.logger.log_item_self import LogItemSelf

        try:
            feedback.save_fields(result.fields)
        except (OSError, ValueError) as error:
            self.notify(str(error), severity="error", timeout=8)
            return
        if not task.config.is_automated:
            task.info.rate = result.rate
        task.info.study = result.study
        task.info.boss = result.boss
        task.info.feedback = True
        self.repo.logger.store(LogItemSelf().set_task(task))
        self.refresh_view()
        self.notify(self._t("Autoavaliação registrada.", "Self evaluation saved."))

    def _ask_delete_task(self, confirm: bool = True) -> None:
        from tko.ui_textual.dialogs import TextInputDialog

        task = self._selected_item()
        if not isinstance(task, Task):
            self.notify("Selecione uma tarefa para excluir.", severity="warning")
            return
        folder = self.repo.task_resolver.target_folder(task)
        if folder is None or not folder.exists():
            self.notify("A tarefa selecionada não possui pasta local.", severity="warning")
            return
        if not confirm:
            self._delete_task(task, folder, task.basic.key)
            return
        self.push_screen(
            TextInputDialog(
                self._t("Excluir tarefa", "Delete task"),
                self._t(f"Digite {task.basic.key} para confirmar:", f"Type {task.basic.key} to confirm:"),
                confirm_label=self._t("Confirmar", "Confirm"),
                cancel_label=self._t("Cancelar", "Cancel"),
            ),
            lambda value: self._delete_task(task, folder, value),
        )

    def _delete_task(self, task: Task, folder: Path, value: str | None) -> None:
        if value != task.basic.key:
            self.notify("A confirmação não corresponde à chave da tarefa.", severity="error")
            return
        import shutil

        try:
            shutil.rmtree(folder)
        except OSError as error:
            self.notify(str(error), severity="error", timeout=8)
            return
        from tko.cmds.drafts_finder_cached import DraftsFinderCached

        DraftsFinderCached.reset_cache()
        self.refresh_view()
        self.notify(self._t("Pasta da tarefa removida.", "Task folder removed."))

    def _ask_draft_title(self) -> None:
        from tko.ui_textual.dialogs import TextInputDialog

        self.push_screen(
            TextInputDialog(
                self._t("Criar rascunho", "Create draft"),
                self._t("Título da tarefa (use @chave para definir a chave):", "Task title (use @key to set its key):"),
                confirm_label=self._t("Confirmar", "Confirm"),
                cancel_label=self._t("Cancelar", "Cancel"),
            ),
            self._create_draft,
        )

    def _create_draft(self, title: str | None) -> None:
        if not title:
            return
        from tko.config.sandbox_drafts import SandboxDrafts
        from tko.feno.indexer import fix_readme

        source = self.repo.data.get_authoring_source()
        if source is None:
            self.notify("Não há uma fonte de autoria configurada.", severity="error")
            return
        index, _ = self.repo.source_resolver.resolve_index_file(source, load_git=False)
        folder = self.repo.source_resolver.source_activity_dir(source)
        folder.mkdir(parents=True, exist_ok=True)
        words = title.split()
        key = next((word[1:] for word in words if word.startswith("@")), "")
        display_title = " ".join(word for word in words if not word.startswith("@")) or "Nova tarefa"
        if not key:
            existing = [entry.name for entry in folder.iterdir()] + [task.basic.key for task in self.repo.game.tasks.values()]
            key = SandboxDrafts.format_draft_key(SandboxDrafts.find_max_numbered_key(existing) + 1)
        destination = folder / key
        if destination.exists():
            self.notify(f"A pasta {destination} já existe.", severity="error")
            return
        destination.mkdir()
        SandboxDrafts.create_sandbox_draft(destination, display_title)
        index.parent.mkdir(parents=True, exist_ok=True)
        if not index.exists():
            index.write_text(f"# {source.name}\n\n", encoding="utf-8")
        fix_readme(index=index, base_dirs=[folder], verbose=False, load_titles=True, yes=True)
        self.action_reload()
        self.notify(f"Rascunho criado em {destination}.")

    def _open_versions(self) -> None:
        task = self._selected_item()
        if not isinstance(task, Task):
            self.notify("Selecione uma tarefa para abrir suas versões.", severity="warning")
            return
        history = self.repo.paths.get_history_task_folder(task.basic.full_key)
        files_root = history / "files"
        files = [path for path in files_root.rglob("*") if path.is_file() and path.suffix in (".json", ".jsonl")] if files_root.exists() else []
        if not files:
            self.notify("Não há versões registradas para esta tarefa.", severity="warning")
            return
        from tko.cli.audit_preview import run_audit_preview

        def open_preview() -> None:
            run_audit_preview(files)

        self._run_after_exit(open_preview)

    def action_activate(self) -> None:
        item = self._selected_item()
        if isinstance(item, Quest):
            if item.basic.full_key in self.model.state.expanded:
                self.model.state.expanded.remove(item.basic.full_key)
            else:
                self.model.state.expanded.add(item.basic.full_key)
            self.refresh_tree()
            return
        if not isinstance(item, Task):
            return
        action = self._task_action(item)
        if action == TaskAction.BAIXAR:
            self._download_task(item)
        elif action == TaskAction.VISITAR:
            self._run_after_exit(lambda: self._open_task_link(item))
        else:
            self._run_after_exit(lambda: self._run_task(item))

    def _task_action(self, task: Task) -> object:
        if task.location.is_non_evaluated and not task.location.is_external:
            return TaskAction.VISITAR
        if task.location.is_non_evaluated and not self.task_formatter.is_downloaded(task):
            return TaskAction.BAIXAR
        if task.location.is_non_evaluated:
            return TaskAction.VISITAR
        if not task.location.is_external:
            return TaskAction.EXECUTAR
        if not self.task_formatter.is_downloaded_for_lang(task):
            return TaskAction.BAIXAR
        return TaskAction.EXECUTAR

    def _download_task(self, task: Task) -> None:
        from tko.cmds.cmd_down import CmdDown
        from tko.logger.log_item_move import LogItemMove, LogItemMoveMode

        report: list[str] = []

        def capture(message: str | RT) -> None:
            text = message.plain() if isinstance(message, RT) else message
            if text:
                report.append(text)

        try:
            downloaded = CmdDown(self.repo, task.basic.full_key, self.settings).set_fnprint(capture).execute()
        except (OSError, ValueError) as error:
            self.notify(str(error), severity="error", timeout=8)
            return

        if not downloaded:
            self.notify(self._t("Não foi possível baixar a tarefa.", "The task could not be downloaded."), severity="error")
            return

        self.repo.logger.store(LogItemMove().set_key(task.basic.full_key).set_mode(LogItemMoveMode.DOWN))
        self.refresh_view()
        self.notify(
            "\n".join(report) or self._t("Tarefa baixada com sucesso.", "Task downloaded successfully."),
            title=self._t("Download da tarefa", "Task download"),
            timeout=12,
            markup=False,
        )

    def _open_task_link(self, task: Task) -> None:
        import webbrowser

        if task.location.is_http_link:
            webbrowser.open(task.location.raw_link)
            return
        if task.location.is_external:
            target = self.repo.task_resolver.target_file(task)
        else:
            target = self.repo.task_resolver.origin_file(task, load_git=True)
        if target is None or not target.exists():
            self.notify("Arquivo da tarefa não encontrado.", severity="warning")
            return
        from tko.play.opener import Opener

        Opener(self.settings).add_files_to_open([target]).open_files()

    def _run_task(self, task: Task) -> None:
        from tko.cmds.cmd_down import CmdDown
        from tko.cmds.cmd_run import Run
        from tko.cmds.default_draft_creator import DefaultDraftCreator
        from tko.cmds.drafts_finder_cached import DraftsFinderCached
        from tko.play.opener import Opener
        from tko.util.param import Param

        folder = self.repo.task_resolver.target_folder(task)
        if folder is None:
            return
        run = Run(self.settings, [folder], Param.Basic(), self.repo.data.lang, self.repo, self.watcher)
        opener = Opener(self.settings).set_language(self.repo.data.lang).add_task_folder_to_open(folder)
        run.set_opener(opener).set_run_without_ask(False).set_tui(True).set_task(self.repo, task)
        run.load()
        if run.context.wdir.solver:
            run.execute()
            return
        if task.location.is_external:
            CmdDown(self.repo, task.basic.full_key, self.settings).execute()
        else:
            _, drafts_folder = DraftsFinderCached(folder, self.repo.data.lang).search_for_solvers()
            DefaultDraftCreator(self.settings).create(drafts_folder, self.repo.data.lang)

    def _run_after_exit(self, callback: Callable[[], None]) -> None:
        self.model.save_state()
        self.settings.save_settings()
        self.exit(result=callback)

    async def action_quit(self) -> None:
        self.model.save_state()
        self.settings.save_settings()
        self.exit()
