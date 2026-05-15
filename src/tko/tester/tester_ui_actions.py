from tko.config.app_settings import ToggleOption
from tko.config.settings import Settings
from tko.floating.floating import Floating
from tko.floating.floating_manager import FloatingManager
from tko.play.opener import Opener
from tko.tester import tester_util
from tko.tester.tester_navigator import TesterNavigator
from tko.tester.tester_palette import TesterPalette
from tko.tester.tester_state import TesterState


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
        self.fman.add_input(
            Floating().bottom().right().set_warning()
            .put_text("Função de travamento {}".format("ligada" if not state.locked_index else "desligada"))
        )
        self.navigator.lock_unit(state)

    def open_editor(self, opener: Opener | None) -> None:
        if opener is not None:
            opener.open_files()

    def change_limit(self, state: TesterState) -> None:
        self.navigator.change_limit(state)
        self.fman.add_input(
            Floating().bottom().right().set_warning()
            .put_text("Limite de execução alterado para {}".format(
                tester_util.get_time_limit_symbol(self.settings.app.timeout)
            ))
        )
        self.settings.save_settings()

    def toggle_diff(self) -> None:
        self.app.toggle_diff()
        self.fman.add_input(
            Floating().bottom().right().set_warning()
            .put_text("Modo de Diff alterado para {}".format(self.app.diff_mode))
        )
        self.settings.save_settings()

    def toggle_borders(self) -> None:
        self.app.toggle(ToggleOption.BORDERS)
        self.fman.add_input(
            Floating().bottom().right().set_warning()
            .put_text("Modo de Bordas alterado para {}".format(
                "ligado" if self.app.use_borders else "desligado"
            ))
        )
        self.settings.save_settings()

    def toggle_images(self) -> None:
        self.app.toggle(ToggleOption.IMAGES)
        self.fman.add_input(
            Floating().bottom().right().set_warning()
            .put_text("Modo de Imagens alterado para {}".format(
                "ligado" if self.app.use_images else "desligado"
            ))
        )
        self.settings.save_settings()

    def open_palette(self, state: TesterState) -> None:
        self.palette.open(state)

    def send_char_not_found(self, key: int) -> None:
        self.fman.add_input(
            Floating().bottom().right().set_error()
            .put_text(f"Tecla char:{chr(key)}, code:{key}, não reconhecida")
        )
