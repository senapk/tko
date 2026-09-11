from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, HorizontalGroup, Vertical, VerticalScroll
from textual.events import Click, Key
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.validation import Function
from textual.widgets import Button, Input, Label, OptionList, RadioButton, RadioSet, Static
from textual.widgets.option_list import Option

from tko.game.feedback import Feedback
from tko.game.task import Task
from tko.game.task_enums import EvalMode


class ConfirmDialog(ModalScreen[bool]):
    """A small modal for destructive actions."""

    DEFAULT_CSS = """ConfirmDialog { align: center middle; } #dialog { width: 60; height: auto; padding: 1 2; border: round $warning; background: $surface; }"""

    def __init__(self, message: str, confirm_label: str = "Confirmar", cancel_label: str = "Cancelar") -> None:
        super().__init__()
        self.message, self.confirm_label, self.cancel_label = message, confirm_label, cancel_label

    def compose(self) -> ComposeResult:
        yield Grid(Label(self.message), Button(self.confirm_label, id="confirm", variant="error"), Button(self.cancel_label, id="cancel"), id="dialog")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")


class TextInputDialog(ModalScreen[str | None]):
    """Validated text input with a typed cancellation result."""

    DEFAULT_CSS = """TextInputDialog { align: center middle; } #dialog { width: 70; height: auto; padding: 1 2; border: round $accent; background: $surface; }"""

    def __init__(
        self,
        title: str,
        prompt: str,
        value: str = "",
        forbidden: Iterable[str] = (),
        confirm_label: str = "Confirmar",
        cancel_label: str = "Cancelar",
    ) -> None:
        super().__init__()
        self.dialog_title: str = title
        self.prompt: str = prompt
        self.value: str = value
        self.confirm_label, self.cancel_label = confirm_label, cancel_label
        values = frozenset(forbidden)
        self.validator = Function(lambda text: text not in values, failure_description="Valor já existe.")

    def compose(self) -> ComposeResult:
        yield Vertical(Label(self.dialog_title), Static(self.prompt), Input(self.value, validators=self.validator, id="value"), Button(self.confirm_label, id="confirm", variant="primary"), Button(self.cancel_label, id="cancel"), id="dialog")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return
        self._submit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "value":
            self._submit()

    def _submit(self) -> None:
        field = self.query_one("#value", Input)
        if field.is_valid:
            self.dismiss(field.value)


class ChoiceDialog(ModalScreen[str | None]):
    """Selection modal for short, keyboard-navigable option lists."""

    DEFAULT_CSS = """
    ChoiceDialog { align: center middle; }
    ChoiceDialog #dialog { width: 60; height: auto; max-height: 80%; padding: 1 2; border: round $accent; background: $surface; }
    ChoiceDialog OptionList { height: auto; max-height: 18; }
    """

    BINDINGS = [("escape", "cancel", "Cancelar")]

    def __init__(self, title: str, options: Iterable[tuple[str, str]], value: str | None = None, hint: str = "↑/↓ ou clique para escolher • Enter seleciona • Esc cancela") -> None:
        super().__init__()
        self.dialog_title: str = title
        self.options: list[tuple[str, str]] = list(options)
        self.value: str | None = value
        self.hint: str = hint

    def compose(self) -> ComposeResult:
        options = [Option(label, id=value) for value, label in self.options]
        yield Vertical(
            Label(self.dialog_title),
            OptionList(*options, id="choice"),
            Static(self.hint),
            id="dialog",
        )

    def on_mount(self) -> None:
        if self.value is None:
            return
        try:
            index = [value for value, _ in self.options].index(self.value)
        except ValueError:
            return
        self.query_one("#choice", OptionList).highlighted = index

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(str(event.option.id))

    def action_cancel(self) -> None:
        self.dismiss(None)


class CommandPalette(ModalScreen[str | None]):
    """Mouse- and keyboard-accessible replacement for the old action palette."""

    DEFAULT_CSS = """
    CommandPalette { align: center middle; }
    CommandPalette #palette-dialog { width: 76; height: auto; max-height: 80%; padding: 1 2; border: round $accent; background: $surface; }
    CommandPalette OptionList { height: auto; max-height: 24; }
    """

    BINDINGS = [("escape", "cancel", "Fechar")]

    def __init__(self, commands: Iterable[tuple[str, str]], title: str = "Actions and settings", hint: str = "↑/↓ or click to choose • Enter runs • Esc closes") -> None:
        super().__init__()
        self.commands: list[tuple[str, str]] = list(commands)
        self.dialog_title: str = title
        self.hint: str = hint

    def compose(self) -> ComposeResult:
        options = [Option(label, id=command) for command, label in self.commands]
        yield Vertical(
            Label(self.dialog_title),
            OptionList(*options, id="commands"),
            Static(self.hint),
            id="palette-dialog",
        )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(str(event.option.id))

    def action_cancel(self) -> None:
        self.dismiss(None)


class PercentageSlider(Static):
    """Keyboard- and mouse-accessible percentage control synchronized with an Input."""

    can_focus = True
    value = reactive(0)
    STEP = 5
    BINDINGS = [
        Binding("left", "decrease", show=False),
        Binding("right", "increase", show=False),
        Binding("home", "minimum", show=False),
        Binding("end", "maximum", show=False),
    ]

    class Changed(Message):
        def __init__(self, slider: PercentageSlider, value: int) -> None:
            super().__init__()
            self.slider = slider
            self.value = value

        @property
        def control(self) -> PercentageSlider:
            return self.slider

    def __init__(self, value: int, disabled: bool = False, id: str | None = None) -> None:
        super().__init__(id=id, disabled=disabled)
        self.value = self._normalize(value)

    @staticmethod
    def _normalize(value: int) -> int:
        return max(0, min(100, value))

    def render(self) -> str:
        width = max(10, self.size.width - 2)
        filled = round(width * self.value / 100)
        return "[" + "█" * filled + "░" * (width - filled) + "]"

    def set_value(self, value: int, emit: bool = False) -> None:
        value = self._normalize(value)
        if value == self.value:
            return
        self.value = value
        if emit:
            self.post_message(self.Changed(self, value))

    def action_decrease(self) -> None:
        self.set_value(self.value - self.STEP, emit=True)

    def action_increase(self) -> None:
        self.set_value(self.value + self.STEP, emit=True)

    def action_minimum(self) -> None:
        self.set_value(0, emit=True)

    def action_maximum(self) -> None:
        self.set_value(100, emit=True)

    def on_click(self, event: Click) -> None:
        width = max(1, self.size.width - 1)
        self.set_value(round(max(0, min(width, event.x)) * 100 / width), emit=True)


class StudyTimeSlider(Static):
    """Discrete study-time picker that persists minutes and presents hours:minutes."""

    can_focus = True
    LEVELS = (5, 10, 20, 30, 45, 60, 80, 100, 120, 150, 180, 210, 240, 270, 300, 360, 420, 480, 540, 600)
    index = reactive(0)
    BINDINGS = [
        Binding("left", "decrease", show=False),
        Binding("right", "increase", show=False),
        Binding("home", "minimum", show=False),
        Binding("end", "maximum", show=False),
    ]

    class Changed(Message):
        def __init__(self, slider: StudyTimeSlider, minutes: int) -> None:
            super().__init__()
            self.slider = slider
            self.minutes = minutes

        @property
        def control(self) -> StudyTimeSlider:
            return self.slider

    def __init__(self, minutes: int, id: str | None = None) -> None:
        super().__init__(id=id)
        self.index = self._nearest_index(minutes)

    @classmethod
    def _nearest_index(cls, minutes: int) -> int:
        return min(range(len(cls.LEVELS)), key=lambda index: (abs(cls.LEVELS[index] - minutes), index))

    @property
    def minutes(self) -> int:
        return self.LEVELS[self.index]

    @staticmethod
    def format_minutes(minutes: int) -> str:
        hours, remainder = divmod(minutes, 60)
        return f"{hours}h{remainder:02d}"

    def render(self) -> str:
        width = max(len(self.LEVELS), self.size.width - 2)
        filled = round(width * (self.index + 1) / len(self.LEVELS))
        return "[" + "█" * filled + "░" * (width - filled) + "]"

    def set_minutes(self, minutes: int, emit: bool = False) -> None:
        self.set_index(self._nearest_index(minutes), emit=emit)

    def set_index(self, index: int, emit: bool = False) -> None:
        index = max(0, min(len(self.LEVELS) - 1, index))
        if index == self.index:
            return
        self.index = index
        if emit:
            self.post_message(self.Changed(self, self.minutes))

    def action_decrease(self) -> None:
        self.set_index(self.index - 1, emit=True)

    def action_increase(self) -> None:
        self.set_index(self.index + 1, emit=True)

    def action_minimum(self) -> None:
        self.set_index(0, emit=True)

    def action_maximum(self) -> None:
        self.set_index(len(self.LEVELS) - 1, emit=True)

    def on_click(self, event: Click) -> None:
        width = max(1, self.size.width - 1)
        self.set_index(round(max(0, min(width, event.x)) * (len(self.LEVELS) - 1) / width), emit=True)


@dataclass(frozen=True)
class GradeResult:
    rate: int
    study: int
    boss: bool
    fields: dict[str, str]


class GradeDialog(ModalScreen[GradeResult | None]):
    """Native form replacing the former Curses floating grade screen."""

    DEFAULT_CSS = """
    GradeDialog { align: center middle; }
    GradeDialog #grade-dialog { width: 90%; height: 90%; padding: 1 2; border: round $success; background: #080808; }
    GradeDialog #grade-error { color: $error; margin: 1 0; }
    GradeDialog #grade-declaration { color: $warning; margin: 1 0; }
    GradeDialog #grade-actions { height: auto; margin-top: 1; }
    GradeDialog #grade-rate-row { height: auto; align-vertical: middle; }
    GradeDialog #grade-rate-row > Label { width: 45; height: 3; content-align: left middle; }
    GradeDialog #grade-slider { width: 1fr; height: 3; padding: 0 1; border: tall $panel; content-align: center middle; }
    GradeDialog #grade-slider:focus { border: tall $accent; background: $primary-muted; text-style: bold; }
    GradeDialog #grade-rate { width: 8; height: 3; margin-left: 1; content-align: center middle; }
    GradeDialog #grade-study-control { height: auto; align-vertical: middle; }
    GradeDialog #grade-study-control > Label { width: 45; height: 3; content-align: left middle; }
    GradeDialog #grade-study-slider { width: 1fr; height: 3; padding: 0 1; border: tall $panel; content-align: center middle; }
    GradeDialog #grade-study-slider:focus { border: tall $accent; background: $primary-muted; text-style: bold; }
    GradeDialog #grade-study { width: 8; height: 3; margin-left: 1; content-align: center middle; }
    GradeDialog .feedback-row { height: auto; align-vertical: middle; }
    GradeDialog .feedback-row > Label { width: 45; height: 3; content-align: left middle; }
    GradeDialog .feedback-row > Input { width: 1fr; min-width: 20; margin-left: 1; }
    GradeDialog .feedback-row > Input { background: #172933; border: tall #3f7185; color: #f1f5f6; }
    GradeDialog .feedback-row > Input:focus { background: #1d3541; border: tall $success; text-style: bold; }
    GradeDialog .feedback-row > Input:disabled { background: #111111; border: tall #303030; color: $text-muted; }
    GradeDialog .feedback-row > Label.missing-required { color: #fbbf24; text-style: bold; }
    GradeDialog #grade-mode-row { height: auto; align-vertical: middle; }
    GradeDialog #grade-mode-row > Label { width: 45; height: 3; content-align: left middle; }
    GradeDialog #grade-mode { layout: horizontal; height: 3; }
    GradeDialog #grade-mode > RadioButton { width: auto; height: 1fr; margin-right: 2; }
    GradeDialog #grade-mode > RadioButton.-on > .toggle--label { background: #166534; color: #f0fff4; text-style: bold; }
    GradeDialog #grade-mode:focus > RadioButton.-selected > .toggle--label { background: #22c55e; color: #06130a; text-style: bold; }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancelar", show=False),
        Binding("ctrl+enter", "submit", "Confirmar", show=False),
    ]

    def __init__(self, task: Task, feedback: Feedback, portuguese: bool = True) -> None:
        super().__init__()
        self.grade_task = task
        self.feedback = feedback
        self.portuguese = portuguese
        try:
            self.fields = feedback.load_fields()
        except ValueError:
            self.fields = {field: "" for field in Feedback.FIELDS}
            self.error_message = self._t(
                "O feedback existente é inválido e será substituído ao confirmar este formulário.",
                "The existing feedback is invalid and will be replaced when this form is confirmed.",
            )
        else:
            self.error_message = ""

    def _t(self, pt: str, en: str) -> str:
        return pt if self.portuguese else en

    def compose(self) -> ComposeResult:
        is_self_evaluation = self.grade_task.config.eval == EvalMode.SELF
        is_diff = self.grade_task.config.is_automated
        with VerticalScroll(id="grade-dialog"):
            yield Label(self._t("Autoavaliação", "Self evaluation"), classes="title")
            yield Static(self.error_message, id="grade-error")
            with HorizontalGroup(id="grade-rate-row"):
                yield Label(
                    self._t("Percentual de testes concluído", "Percentage of tests completed")
                    if is_diff
                    else self._t("Informe o percentual concluído", "Enter the completion percentage")
                )
                yield PercentageSlider(self.grade_task.info.rate, disabled=not is_self_evaluation, id="grade-slider")
                yield Static(f"{self.grade_task.info.rate}%", id="grade-rate")
            with HorizontalGroup(id="grade-study-control"):
                yield Label(self._t("Tempo total de estudo e código:", "Total study and coding time:"))
                study_slider = StudyTimeSlider(self.grade_task.info.study, id="grade-study-slider")
                yield study_slider
                yield Static(StudyTimeSlider.format_minutes(study_slider.minutes), id="grade-study")
            with HorizontalGroup(id="grade-mode-row"):
                yield Label(self._t("Modo de avaliação", "Evaluation mode"))
                yield RadioSet(
                    RadioButton(self._t("Estudo", "Study"), value=not self.grade_task.info.boss, id="grade-study-mode"),
                    RadioButton(self._t("Avaliação", "Evaluation"), value=self.grade_task.info.boss, id="grade-boss-mode"),
                    id="grade-mode",
            )
            yield Static(id="grade-declaration")
            labels = self._field_labels()
            for field in ("what", "how", "tools", "learned"):
                yield self._feedback_section(field, labels[field])
            with Horizontal(id="grade-actions"):
                yield Button(self._t("Cancelar", "Cancel"), id="grade-cancel")
                yield Button(self._t("Confirmar", "Confirm"), id="grade-confirm", variant="success")

    def _field_labels(self) -> dict[str, str]:
        return {
            "what": self._t("O que fez ou falta fazer?", "What did you do or still need to do?"),
            "how": self._t("Como e/ou com quem você realizou?", "How and/or with whom did you complete it?"),
            "tools": self._t("Ferramentas e recursos usados, incluindo IA", "Tools and resources used, including AI"),
            "learned": self._t("O que você aprendeu e ainda precisa estudar?", "What did you learn and still need to study?"),
        }

    def _feedback_section(self, field: str, label: str) -> HorizontalGroup:
        return HorizontalGroup(
            Label(label, id=f"feedback-label-{field}"),
            Input(self.fields[field].replace("\n", " "), id=f"feedback-{field}", placeholder=label),
            id=f"feedback-section-{field}",
            classes="feedback-row",
        )

    def on_mount(self) -> None:
        self._refresh_form_state()
        if self.grade_task.config.eval == EvalMode.SELF:
            self.query_one("#grade-slider", PercentageSlider).focus()
        else:
            self.query_one("#grade-study-slider", StudyTimeSlider).focus()

    def on_radio_set_changed(self, _: RadioSet.Changed) -> None:
        self._refresh_form_state()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id in {"feedback-what", "feedback-how", "feedback-tools", "feedback-learned"}:
            self._refresh_form_state()

    def on_percentage_slider_changed(self, event: PercentageSlider.Changed) -> None:
        self.query_one("#grade-rate", Static).update(f"{event.value}%")
        self._refresh_form_state()

    def on_study_time_slider_changed(self, event: StudyTimeSlider.Changed) -> None:
        self.query_one("#grade-study", Static).update(StudyTimeSlider.format_minutes(event.minutes))
        self._refresh_form_state()

    def on_key(self, event: Key) -> None:
        """Provide consistent keyboard traversal without stealing slider arrows."""
        if event.key in {"tab", "down"}:
            event.stop()
            self.focus_next()
            return
        if event.key in {"shift+tab", "up"}:
            event.stop()
            self.focus_previous()
            return
        if event.key != "enter" or isinstance(self.focused, Button):
            return
        event.stop()
        if isinstance(self.focused, RadioSet):
            self.focused.action_toggle_button()
            self._refresh_form_state()
        self.focus_next()

    def _field_values(self) -> dict[str, str]:
        return {field: self._feedback_editor(field).value for field in Feedback.FIELDS}

    def _feedback_editor(self, field: str) -> Input:
        return self.query_one(f"#feedback-{field}", Input)

    def _active_fields(self) -> tuple[str, ...]:
        rate = self._rate_value()
        boss = self.query_one("#grade-boss-mode", RadioButton).value
        fields: list[str] = []
        if rate != 100:
            fields.append("what")
        if not boss:
            fields.extend(("how", "tools"))
        fields.append("learned")
        return tuple(fields)

    def _sync_field_state(self, active_fields: tuple[str, ...]) -> None:
        labels = self._field_labels()
        for field in Feedback.FIELDS:
            label = self.query_one(f"#feedback-label-{field}", Label)
            editor = self._feedback_editor(field)
            if field in active_fields:
                label.update(labels[field])
                editor.disabled = False
                if editor.value == "---":
                    editor.value = ""
            else:
                label.update(labels[field])
                if editor.value != "---":
                    editor.value = "---"
                editor.disabled = True

    def _study_value(self) -> int | None:
        return self.query_one("#grade-study-slider", StudyTimeSlider).minutes

    def _rate_value(self) -> int | None:
        return self.query_one("#grade-slider", PercentageSlider).value

    def _refresh_form_state(self) -> None:
        boss = self.query_one("#grade-boss-mode", RadioButton).value
        declaration = (
            self._t(
                "Escolhendo avaliação, você declara que realizou esta atividade em condições de avaliação: sem pesquisas, ajuda de outras pessoas ou ferramentas de IA. Todo o trabalho entregue, mesmo que parcial, deve ter sido produzido exclusivamente a partir do seu próprio conhecimento, usando apenas tentativa e erro.",
                "By choosing evaluation, you declare that you performed this activity under evaluation conditions, without research, help from other people, or AI tools. All work submitted, even if partial, must have been produced exclusively from your own knowledge, using only trial and error.",
            )
            if boss
            else self._t(
                "Escolhendo estudo, você declara que realizou esta atividade em condições de estudo, nas quais são permitidas pesquisas, ajuda de outras pessoas e ferramentas de IA. O objetivo é aprender e concluir a atividade, podendo utilizar recursos externos para compreender o conteúdo ou resolver as dificuldades encontradas.",
                "By choosing study, you declare that you performed this activity under study conditions, where research, help from other people, and AI tools are allowed. The goal is to learn and complete the activity, and you may use external resources to understand the content or overcome difficulties encountered.",
            )
        )
        self.query_one("#grade-declaration", Static).update(declaration)
        active_fields = self._active_fields()
        self._sync_field_state(active_fields)
        values = self._field_values()
        missing_fields = tuple(field for field in active_fields if not values[field].strip())
        for field in Feedback.FIELDS:
            missing = field in missing_fields
            self.query_one(f"#feedback-label-{field}", Label).set_class(missing, "missing-required")
        valid = not missing_fields and self._rate_value() is not None and self._study_value() is not None
        self.query_one("#grade-confirm", Button).disabled = not valid

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "grade-cancel":
            self.dismiss(None)
        elif event.button.id == "grade-confirm":
            self._submit()

    def _submit(self) -> None:
        study = self._study_value()
        rate = self._rate_value()
        active_fields = self._active_fields()
        raw_fields = self._field_values()
        fields = {field: raw_fields[field] if field in active_fields else "" for field in Feedback.FIELDS}
        if rate is None or study is None or not all(fields[field].strip() for field in active_fields):
            self._refresh_form_state()
            return
        boss = self.query_one("#grade-boss-mode", RadioButton).value
        self.dismiss(GradeResult(rate, study, boss, fields))

    def action_submit(self) -> None:
        self._submit()

    def action_cancel(self) -> None:
        self.dismiss(None)
