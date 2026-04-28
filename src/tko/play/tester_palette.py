from tko.config.app_settings import AppSettings, ToggleOption
from tko.play.floating import Floating
from tko.play.floating_drop_down import FloatingDropDown, FloatingInputData
from tko.play.floating_manager import FloatingManager
from tko.play.keys import GuiKeys
from tko.play.tester_navigator import TesterNavigator
from tko.play.tester_state import TesterState
from tko.play import tester_util
from tko.util.rtext import RText
from tko.util.symbols import Symbols


class TesterPalette:

    def __init__(
        self,
        app: AppSettings,
        fman: FloatingManager,
        navigator: TesterNavigator,
    ) -> None:
        self.app = app
        self.fman = fman
        self.navigator = navigator

    def open(self, state: TesterState) -> None:
        def icon(value: bool) -> str:
            return "✓" if value else "✗"

        options: list[FloatingInputData] = [
            FloatingInputData(
                lambda: RText.format(" {} Mudar arquivo {y} de execução", Symbols.action, "principal"),
                lambda: self.navigator.change_main(state),
                "TAB",
            ),
            FloatingInputData(
                lambda: RText.format(" {} Mudar modo {y}}", tester_util.get_diff_symbol(self.app.diff_mode), "Diff"),
                self.app.toggle_diff,
                GuiKeys.diff,
            ),
            FloatingInputData(
                lambda: RText.format(
                    " {} Mudar {y} de tempo de execução: {r}",
                    Symbols.action, "Limite",
                    tester_util.get_time_limit_symbol(self.app.timeout),
                ),
                lambda: self.navigator.change_limit(state),
                GuiKeys.limite,
            ),
            FloatingInputData(
                lambda: RText.format(
                    " {} Testar {y} os casos ou apenas o selecionado",
                    icon(not state.locked_index), "Todos",
                ),
                lambda: self.navigator.lock_unit(state),
                GuiKeys.lock,
            ),
            FloatingInputData(
                lambda: RText.format(" {} Mostrar {y}", icon(self.app.use_borders), "Bordas"),
                lambda: self.app.toggle(ToggleOption.BORDERS),
                GuiKeys.borders,
            ),
            FloatingInputData(
                lambda: RText.format(" {} Mostrar {y}", icon(self.app.use_images), "Imagens"),
                lambda: self.app.toggle(ToggleOption.IMAGES),
                GuiKeys.images,
            ),
            FloatingInputData(
                lambda: RText.format(" {} Tarefa: Auto {y} método de estudo", Symbols.action, "Avaliar"),
                lambda: self.navigator.self_evaluate(state),
                GuiKeys.self_evaluate,
            ).set_exit_on_action(True),
        ]

        self.fman.add_input(
            FloatingDropDown()
            .set_floating(
                Floating()
                .set_text_ljust()
                .set_header(" Selecione uma ação da lista ")
                .set_footer(" Use Enter para aplicar e Esc para Sair ")
            )
            .set_options(options)
            .set_exit_on_enter(False)
        )
