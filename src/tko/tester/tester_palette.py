from tko.config.app_settings import AppSettings, ToggleOption
from tko.floating.floating import Floating
from tko.floating.floating_drop_down import FloatingDropDown, FloatingInputData
from tko.floating.floating_manager import FloatingManager
from tko.play.gui_keys import GuiKeys
from tko.tester.tester_navigator import TesterNavigator
from tko.tester.tester_state import TesterState
from tko.tester import tester_util
from tko.i18n import Msg, t
from tko.util.rt import RT
from tko.util.symbols import Symbols



_ALL = Msg(pt="[y]Todos[]", en="[y]All[]")
_IMAGES_LABEL = Msg(pt="[y]Imagens[]", en="[y]Images[]")
_EVALUATE_LABEL = Msg(pt="[y]Avaliar[]", en="[y]Evaluate[]")
_HEADER = Msg( pt=" Selecione uma ação da lista ", en=" Select an action from the list ")
_FOOTER = Msg( pt=" Use Enter para aplicar e Esc para Sair ", en=" Use Enter to apply and Esc to exit " )
_CHANGE_MAIN = Msg( pt=" {icon} Mudar arquivo [y]principal[]", en=" {icon} Change [y]main[] execution file" )
_DIFF_MODE = Msg( pt=" {icon} Mudar modo [y]Diff[]", en=" {icon} Change mode [y]Diff[]" )
_LIMIT = Msg( pt=" {icon} Mudar limite de tempo de execução para [y]{valor}[]", en=" {icon} Change execution time limit to [y]{valor}[]" )
_TEST_SCOPE = Msg( pt=" {icon} Testar casos ou apenas o selecionado", en=" {icon} Test all cases or only the selected one" )
_SHOW_IMAGES = Msg( pt=" {icon} Mostrar imagens após passar nos testes", en=" {icon} Show images after passing tests" )
_EVALUATE = Msg( pt=" {icon} Auto [y]avaliar[] método de estudo", en=" {icon} Self [y]evaluate[] study method" )

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
                lambda: RT.parse(t(_CHANGE_MAIN).format(icon=Symbols.action)),
                lambda: self.navigator.change_main(state),
                "TAB",
            ))
        options.append(FloatingInputData(
                lambda: RT.parse(t(_DIFF_MODE).format(icon=tester_util.get_diff_symbol(self.app.diff_mode))),
                self.app.toggle_diff,
                GuiKeys.diff,
            ))
        options.append(FloatingInputData(
                lambda: RT.parse(t(_LIMIT).format(icon=Symbols.action, valor=tester_util.get_time_limit_symbol(self.app.timeout))),
                lambda: self.navigator.change_limit(state),
                GuiKeys.limite,
            ))
        options.append(FloatingInputData(
                lambda: RT.parse(t(_TEST_SCOPE).format(icon=mark(not state.locked_index))),
                lambda: self.navigator.lock_unit(state),
                GuiKeys.lock,
            ))
        options.append(FloatingInputData(
                lambda: RT.parse(t(_IMAGES_LABEL).format(icon=mark(self.app.use_images))),
                lambda: self.app.toggle(ToggleOption.IMAGES),
                GuiKeys.images,
            ))
        options.append(FloatingInputData(
                lambda: RT.parse(t(_EVALUATE).format(icon=Symbols.action)),
                lambda: self.navigator.self_evaluate(state),
                GuiKeys.self_evaluate,
            ).set_exit_on_action(True)
            )
        obj = (
            FloatingDropDown()
            .set_floating(
                Floating()
                .set_text_ljust()
                .set_header_text(RT.parse(t(_HEADER)))
                .set_footer_text(RT.parse(t(_FOOTER)))
            )
            .set_options(options)
            .set_exit_on_enter(False)
        )
        obj.id = "palette"
        self.fman.add_input(obj)
