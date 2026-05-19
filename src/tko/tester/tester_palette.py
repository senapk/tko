from tko.config.app_settings import AppSettings, ToggleOption
from tko.floating.floating import Floating
from tko.floating.floating_drop_down import FloatingDropDown, FloatingInputData
from tko.floating.floating_manager import FloatingManager
from tko.play.keys import GuiKeys
from tko.tester.tester_navigator import TesterNavigator
from tko.tester.tester_state import TesterState
from tko.tester import tester_util
from tko.i18n import MsgRT, tr
from tko.util.rt import RT
from tko.util.symbols import Symbols


class _PaletteMsg:
    MAIN_FILE = MsgRT(pt=RT("principal", "y"), en=RT("main", "y"))
    DIFF = MsgRT(pt=RT("Diff", "y"), en=RT("Diff", "y"))
    LIMIT = MsgRT(pt=RT("Limite", "y"), en=RT("Limit", "y"))
    ALL = MsgRT(pt=RT("Todos", "y"), en=RT("All", "y"))
    IMAGES_LABEL = MsgRT(pt=RT("Imagens", "y"), en=RT("Images", "y"))
    EVALUATE_LABEL = MsgRT(pt=RT("Avaliar", "y"), en=RT("Evaluate", "y"))
    HEADER = MsgRT(
        pt=RT(" Selecione uma ação da lista "),
        en=RT(" Select an action from the list "),
    )
    FOOTER = MsgRT(
        pt=RT(" Use Enter para aplicar e Esc para Sair "),
        en=RT(" Use Enter to apply and Esc to exit "),
    )
    @staticmethod
    def change_main(action: str) -> MsgRT:
        return MsgRT(
            pt=RT.parse(" <$> Mudar arquivo <$> de execução", action, _PaletteMsg.MAIN_FILE.pt),
            en=RT.parse(" <$> Change <$> execution file", action, _PaletteMsg.MAIN_FILE.en),
        )

    @staticmethod
    def diff_mode(symbol: str) -> MsgRT:
        return MsgRT(
            pt=RT.parse(" <$> Mudar modo <$>", symbol, _PaletteMsg.DIFF.pt),
            en=RT.parse(" <$> Change mode <$>", symbol, _PaletteMsg.DIFF.en),
        )

    @staticmethod
    def time_limit(action: str, value: RT) -> MsgRT:
        return MsgRT(
            pt=RT.parse(" <$> Mudar <$> de tempo de execução: <$>", action, _PaletteMsg.LIMIT.pt, value),
            en=RT.parse(" <$> Change <$> execution time limit: <$>", action, _PaletteMsg.LIMIT.en, value),
        )

    @staticmethod
    def test_scope(icon_value: str) -> MsgRT:
        return MsgRT(
            pt=RT.parse(" <$> Testar [y]<$>[] os casos ou apenas o selecionado", icon_value, _PaletteMsg.ALL.pt),
            en=RT.parse(" <$> Test [y]<$>[] all cases or only the selected one", icon_value, _PaletteMsg.ALL.en),
        )

    @staticmethod
    def images(icon_value: str) -> MsgRT:
        return MsgRT(
            pt=RT.parse(" <$> Mostrar [y]<$>[]", icon_value, _PaletteMsg.IMAGES_LABEL.pt),
            en=RT.parse(" <$> Show [y]<$>[]", icon_value, _PaletteMsg.IMAGES_LABEL.en),
        )

    @staticmethod
    def self_evaluate(action: str) -> MsgRT:
        return MsgRT(
            pt=RT.parse(" <$> Tarefa: Auto <$> método de estudo", action, _PaletteMsg.EVALUATE_LABEL.pt),
            en=RT.parse(" <$> Task: Self-<$> study method", action, _PaletteMsg.EVALUATE_LABEL.en),
        )


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
                lambda: tr(_PaletteMsg.change_main(Symbols.action)),
                lambda: self.navigator.change_main(state),
                "TAB",
            ),
            FloatingInputData(
                lambda: tr(_PaletteMsg.diff_mode(tester_util.get_diff_symbol(self.app.diff_mode))),
                self.app.toggle_diff,
                GuiKeys.diff,
            ),
            FloatingInputData(
                lambda: tr(_PaletteMsg.time_limit(
                    Symbols.action,
                    RT.run("r", tester_util.get_time_limit_symbol(self.app.timeout)),
                )),
                lambda: self.navigator.change_limit(state),
                GuiKeys.limite,
            ),
            FloatingInputData(
                lambda: tr(_PaletteMsg.test_scope(icon(not state.locked_index))),
                lambda: self.navigator.lock_unit(state),
                GuiKeys.lock,
            ),
            FloatingInputData(
                lambda: tr(_PaletteMsg.images(icon(self.app.use_images))),
                lambda: self.app.toggle(ToggleOption.IMAGES),
                GuiKeys.images,
            ),
            FloatingInputData(
                lambda: tr(_PaletteMsg.self_evaluate(Symbols.action)),
                lambda: self.navigator.self_evaluate(state),
                GuiKeys.self_evaluate,
            ).set_exit_on_action(True),
        ]

        self.fman.add_input(
            FloatingDropDown()
            .set_floating(
                Floating()
                .set_text_ljust()
                .set_header_text(tr(_PaletteMsg.HEADER))
                .set_footer_text(tr(_PaletteMsg.FOOTER))
            )
            .set_options(options)
            .set_exit_on_enter(False)
        )
