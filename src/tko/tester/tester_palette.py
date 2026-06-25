from tko.config.app_settings import AppSettings, ToggleOption
from tko.floating.floating import Floating
from tko.floating.floating_drop_down import FloatingDropDown, FloatingInputData
from tko.floating.floating_manager import FloatingManager
from tko.play.gui_keys import GuiKeys
from tko.tester.tester_navigator import TesterNavigator
from tko.tester.tester_state import TesterState
from tko.tester import tester_util
from tko.i18n import Msg
from tko.util.symbols import Symbols



_ALL = Msg.parse(pt="[y]Todos[]", en="[y]All[]")
_IMAGES_LABEL = Msg.parse(pt="[y]Imagens[]", en="[y]Images[]")
_EVALUATE_LABEL = Msg.parse(pt="[y]Avaliar[]", en="[y]Evaluate[]")
_HEADER = Msg.parse( pt=" Selecione uma ação da lista ", en=" Select an action from the list ")
_FOOTER = Msg.parse( pt=" Use Enter para aplicar e Esc para Sair ", en=" Use Enter to apply and Esc to exit " )
_CHANGE_MAIN = Msg.parse( pt=" {icon} Mudar arquivo [y]principal[]", en=" {icon} Change [y]main[] execution file" )
_DIFF_MODE = Msg.parse( pt=" {icon} Mudar modo [y]Diff[]", en=" {icon} Change mode [y]Diff[]" )
_LIMIT = Msg.parse( pt=" {icon} Mudar limite de tempo de execução para [y]{valor}[]", en=" {icon} Change execution time limit to [y]{valor}[]" )
_TEST_SCOPE = Msg.parse( pt=" {icon} Testar casos ou apenas o selecionado", en=" {icon} Test all cases or only the selected one" )
_SHOW_IMAGES = Msg.parse( pt=" {icon} Mostrar imagens após passar nos testes", en=" {icon} Show images after passing tests" )
_EVALUATE = Msg.parse( pt=" {icon} Auto [y]avaliar[] método de estudo", en=" {icon} Self [y]evaluate[] study method" )

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
        def mark(value: bool) -> str:
            return "✓" if value else "✗"

        options: list[FloatingInputData] = []
        options.append(FloatingInputData(
                lambda: _CHANGE_MAIN.t().format(icon=Symbols.action),
                lambda: self.navigator.change_main(state),
                "TAB",
            ))
        options.append(FloatingInputData(
                lambda: _DIFF_MODE.t().format(icon=tester_util.get_diff_symbol(self.app.diff_mode)),
                self.app.toggle_diff,
                GuiKeys.diff,
            ))
        options.append(FloatingInputData(
                lambda: _LIMIT.t().format(icon=Symbols.action, valor=tester_util.get_time_limit_symbol(self.app.timeout)),
                lambda: self.navigator.change_limit(state),
                GuiKeys.limite,
            ))
        options.append(FloatingInputData(
                lambda: _TEST_SCOPE.t().format(icon=mark(not state.locked_index)),
                lambda: self.navigator.lock_unit(state),
                GuiKeys.lock,
            ))
        options.append(FloatingInputData(
                lambda: _SHOW_IMAGES.t().format(icon=mark(self.app.use_images)),
                lambda: self.app.toggle(ToggleOption.IMAGES),
                GuiKeys.images,
            ))
        options.append(FloatingInputData(
                lambda: _EVALUATE.t().format(icon=Symbols.action),
                lambda: self.navigator.self_evaluate(state),
                GuiKeys.self_evaluate,
            ).set_exit_on_action(True)
            )
        obj = (
            FloatingDropDown()
            .set_floating(
                Floating()
                .set_text_ljust()
                .set_header_rt(_HEADER.t())
                .set_footer_rt(_FOOTER.t())
            )
            .set_options(options)
            .set_exit_on_enter(False)
            .set_id("palette")
        )
        self.fman.add_floating(obj)
