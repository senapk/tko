"""One-task comparison across all student repositories."""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Input, Static

from tko.play.review_overview import ReviewOverviewService, ReviewTaskRow


class ReviewOverviewScreen(Screen[int | None]):
    CSS = """
    ReviewOverviewScreen { layout: vertical; }
    #class-title, #class-status, #class-detail { height: 1; padding: 0 1; }
    #class-title { background: $primary; color: $background; text-style: bold; }
    #class-filter { height: 3; }
    #class-table { height: 1fr; }
    """
    BINDINGS = [
        Binding("escape", "close_overview", "Voltar"),
        Binding("slash", "focus_filter", "Filtrar"),
        Binding("r", "reload_rows", "Atualizar"),
        Binding("e", "export_rows", "Exportar CSV"),
    ]

    def __init__(self, service: ReviewOverviewService, task_key: str, current_index: int) -> None:
        super().__init__()
        self.service: ReviewOverviewService = service
        self.task_key: str = task_key
        self.current_index: int = current_index
        self.rows: dict[int, ReviewTaskRow] = {}
        self.visible_indices: list[int] = []
        self.loaded: bool = False
        self.sort_column: str = "student"
        self.sort_descending: bool = False
        self._pending_export: Path | None = None

    def compose(self) -> ComposeResult:
        yield Static(f"Turma · {self.task_key}", id="class-title")
        yield Static("Carregando repositórios...", id="class-status")
        yield Input(placeholder="Filtrar alunos; / foca a busca", id="class-filter")
        yield DataTable[str](id="class-table", cursor_type="row", zebra_stripes=True)
        yield Static("Enter abre o aluno · Esc volta", id="class-detail")
        yield Footer()

    def on_mount(self) -> None:
        table: DataTable[str] = self.query_one("#class-table", DataTable)
        for label, key in (
            ("Aluno", "student"), ("Situação", "status"), ("Avaliação", "grade"),
            ("Exec.", "executions"), ("Versões", "versions"),
            ("Tempo (min)", "minutes"), ("Último evento", "last_event"),
        ):
            table.add_column(label, key=key)
        table.focus()
        self.run_worker(self._load_rows(), exclusive=True)

    async def _load_rows(self, *, refresh: bool = False) -> None:
        self.loaded = False
        self.rows.clear()
        self._render_rows()
        total: int = len(self.service.repositories)
        for index in range(total):
            row: ReviewTaskRow = await asyncio.to_thread(self.service.row, self.task_key, index, refresh=refresh)
            if not self.is_mounted:
                return
            self.rows[index] = row
            self.query_one("#class-status", Static).update(f"{len(self.rows)}/{total} repositórios carregados")
            self._render_rows()
        self.loaded = True
        errors: int = sum(row.status == "erro" for row in self.rows.values())
        suffix: str = f" · {errors} com erro" if errors else ""
        self.query_one("#class-status", Static).update(f"{total} alunos · {self.task_key}{suffix}")

    def _sort_key(self, row: ReviewTaskRow) -> str | float:
        if self.sort_column == "grade":
            return -1.0 if row.grade is None else row.grade
        if self.sort_column == "executions":
            return float(row.executions)
        if self.sort_column == "versions":
            return float(row.versions)
        if self.sort_column == "minutes":
            return row.minutes
        if self.sort_column == "last_event":
            return row.last_event.isoformat() if row.last_event is not None else ""
        if self.sort_column == "status":
            return row.status
        return row.student.casefold()

    def _render_rows(self) -> None:
        table: DataTable[str] = self.query_one("#class-table", DataTable)
        previous_indices: list[int] = self.visible_indices
        selected_index: int | None = None
        if table.row_count and 0 <= table.cursor_row < len(self.visible_indices):
            selected_index = self.visible_indices[table.cursor_row]
        table.clear()
        query: str = self.query_one("#class-filter", Input).value.casefold()
        ordered: list[ReviewTaskRow] = sorted(
            self.rows.values(), key=self._sort_key, reverse=self.sort_descending,
        )
        self.visible_indices = []
        for row in ordered:
            if query and query not in row.student.casefold():
                continue
            self.visible_indices.append(row.index)
            table.add_row(
                row.student, row.status,
                "—" if row.grade is None else f"{row.grade:.0f}%",
                str(row.executions), str(row.versions), f"{row.minutes:.1f}",
                row.last_event.strftime("%d/%m %H:%M") if row.last_event is not None else "—",
                key=str(row.index),
            )
        candidates: tuple[int | None, ...] = (
            (self.current_index, selected_index)
            if self.current_index not in previous_indices
            else (selected_index, self.current_index)
        )
        for index in candidates:
            if index in self.visible_indices:
                table.move_cursor(row=self.visible_indices.index(index))
                break

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "class-filter":
            self._render_rows()

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        column: str = str(event.column_key.value)
        self.sort_descending = not self.sort_descending if self.sort_column == column else False
        self.sort_column = column
        self._render_rows()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if 0 <= event.cursor_row < len(self.visible_indices):
            row: ReviewTaskRow = self.rows[self.visible_indices[event.cursor_row]]
            self.query_one("#class-detail", Static).update(row.error or str(row.repository))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if 0 <= event.cursor_row < len(self.visible_indices):
            self.dismiss(self.visible_indices[event.cursor_row])

    def action_close_overview(self) -> None:
        self.dismiss(None)

    def action_focus_filter(self) -> None:
        self.query_one("#class-filter", Input).focus()

    def action_reload_rows(self) -> None:
        self.run_worker(self._load_rows(refresh=True), exclusive=True)

    def action_export_rows(self) -> None:
        if not self.loaded:
            self.app.notify("Aguarde o carregamento da turma.", severity="warning")
            return
        from tko.ui_textual.dialogs import TextInputDialog

        safe_key: str = self.task_key.replace("@", "_").replace("/", "_")
        default: Path = self.service.repositories[0].parent / f"turma-{safe_key}.csv"
        self.app.push_screen(
            TextInputDialog("Exportar CSV", "Caminho do arquivo:", value=str(default)),
            self._choose_export_path,
        )

    def _choose_export_path(self, value: str | None) -> None:
        if not value:
            return
        path: Path = Path(value).expanduser()
        if not path.is_absolute():
            path = self.service.repositories[0].parent / path
        if path.exists():
            from tko.ui_textual.dialogs import ConfirmDialog

            self._pending_export = path
            self.app.push_screen(
                ConfirmDialog(f"Substituir {path}?"), self._confirm_export,
            )
        else:
            self._write_export(path)

    def _confirm_export(self, confirmed: bool | None) -> None:
        path: Path | None = self._pending_export
        self._pending_export = None
        if confirmed and path is not None:
            self._write_export(path)

    def _write_export(self, path: Path) -> None:
        try:
            rows: list[ReviewTaskRow] = [self.rows[index] for index in range(len(self.service.repositories))]
            self.service.export_csv(path, self.task_key, rows)
        except OSError as error:
            self.app.notify(str(error), severity="error", timeout=8)
            return
        self.app.notify(f"CSV salvo em {path}")
