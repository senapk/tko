from tko.config.app_settings import ToggleOption
from tko.config.settings import Settings
from tko.floating.floating import Floating
from tko.floating.floating_manager import FloatingManager
from tko.i18n import Msg
from tko.play.opener import Opener
from tko.tester import tester_util
from tko.tester.tester_navigator import TesterNavigator
from tko.tester.tester_palette import TesterPalette
from tko.tester.tester_state import TesterState


class _TesterUiActionsMsg:
    LOCK_TOGGLE = Msg(pt="Função de travamento {}", en="Lock function {}")
    LOCK_ON = Msg(pt="ligada", en="enabled")
    LOCK_OFF = Msg(pt="desligada", en="disabled")

    LIMIT_CHANGED = Msg(pt="Limite de execução alterado para {}", en="Execution limit changed to {}")

    DIFF_MODE_CHANGED = Msg(pt="Modo de Diff alterado para {}", en="Diff mode changed to {}")

    IMAGES_MODE_CHANGED = Msg(pt="Modo de Imagens alterado para {}", en="Image mode changed to {}")
    IMAGES_ON = Msg(pt="ligado", en="enabled")
    IMAGES_OFF = Msg(pt="desligado", en="disabled")

    CHAR_NOT_FOUND = Msg(pt="Tecla char:{}, code:{}, não reconhecida", en="Key char:{}, code:{}, not recognized")


class TesterUiActions:
    def __init__(
        self,
        settings: Settings,
        fman: FloatingManager,
        navigator: TesterNavigator,
        palette: TesterPalette,
    ) -> None:
        self.settings = settings
        self.app = settings.app
        self.fman = fman
        self.navigator = navigator
        self.palette = palette

    def toggle_lock(self, state: TesterState) -> None:
        self.fman.add_floating(
            Floating().bottom().right().set_warning().set_countdown(Floating.Time.FAST)
            .put_text(
                str(_TesterUiActionsMsg.LOCK_TOGGLE).format(
                    str(_TesterUiActionsMsg.LOCK_ON) if not state.locked_index else str(_TesterUiActionsMsg.LOCK_OFF)
                )
            )
        )
        self.navigator.lock_unit(state)

    def open_editor(self, opener: Opener | None) -> None:
        if opener is not None:
            opener.open_files()

    def change_limit(self, state: TesterState) -> None:
        self.navigator.change_limit(state)
        self.fman.add_floating(
            Floating().bottom().right().set_warning().set_countdown(Floating.Time.FAST)
            .put_text(
                str(_TesterUiActionsMsg.LIMIT_CHANGED).format(
                    tester_util.get_time_limit_symbol(self.settings.app.timeout)
                )
            )
        )
        self.settings.save_settings()

    def toggle_diff(self) -> None:
        self.app.toggle_diff()
        self.fman.add_floating(
            Floating().bottom().right().set_warning().set_countdown(Floating.Time.FAST)
            .put_text(str(_TesterUiActionsMsg.DIFF_MODE_CHANGED).format(self.app.diff_mode.value))
        )
        self.settings.save_settings()

    def toggle_images(self) -> None:
        self.app.toggle(ToggleOption.IMAGES)
        self.fman.add_floating(
            Floating().bottom().right().set_warning().set_countdown(Floating.Time.FAST)
            .put_text(
                str(_TesterUiActionsMsg.IMAGES_MODE_CHANGED).format(
                    str(_TesterUiActionsMsg.IMAGES_ON) if self.app.use_images else str(_TesterUiActionsMsg.IMAGES_OFF)
                )
            )
        )
        self.settings.save_settings()

    def open_palette(self, state: TesterState) -> None:
        self.palette.open(state)

    def send_char_not_found(self, key: int) -> None:
        self.fman.add_floating(
            Floating().bottom().right().set_error()
            .put_text(str(_TesterUiActionsMsg.CHAR_NOT_FOUND).format(chr(key), key)).set_countdown(Floating.Time.FAST)
        )
