from tko.play.floating_drop_down import FloatingDropDown
from tko.play.floating_drop_down import FloatingInputData
from tko.settings.app_settings import ToggleOption
from tko.util.text import Text
from tko.util.symbols import Symbols
from tko.play.keys import GuiKeys
from tko.play.play_actions import PlayActions
from tko.play.floating_calibrate import FloatingCalibrate
from tko.play.floating import Floating

class PlayPalette:
    def __init__(self, actions: PlayActions):
        self.actions = actions
        self.flags = self.actions.repo.flags
        self.app = self.actions.settings.app
        self.fman = self.actions.fman
        self.gui = self.actions.gui

    def command_pallete(self):
        options: list[FloatingInputData] = []

        def icon(value: bool):
            return Text.Token("✓", "g") if value else Text.Token("✗", "r")
        
        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Tarefa: {y} para o repositório", Symbols.action, "Baixar"),
                self.actions.down_remote_task,
                GuiKeys.down_task
            ).set_exit_on_action(True)
        )

        # self evaluate
        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Tarefa: Auto {y} método de estudo", Symbols.action, "Avaliar"),
                self.actions.self_evaluate,
                GuiKeys.self_evaluate
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Tarefa: {y} pasta", Symbols.action, "Apagar"),
                self.actions.delete_folder_ask,
                GuiKeys.delete_folder
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y}", Symbols.action, "Ajuda"),
                lambda: self.flags.panel.set_help(),
                GuiKeys.panel_help
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y}", icon(self.app.use_borders), "Bordas"),
                lambda: self.app.toggle(ToggleOption.BORDERS),
                GuiKeys.borders
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y}", icon(self.app.use_images), "Imagens"),
                lambda: self.app.toggle(ToggleOption.IMAGES),
                GuiKeys.images
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y} decorrido", icon(self.flags.show_time.is_true()), "Tempo"),
                lambda: self.flags.show_time.toggle(),
                GuiKeys.show_duration
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mudar {y} de programação", Symbols.action, "Linguagem"),
                self.gui.language.set_language,
                GuiKeys.set_lang_drafts
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} {y} as teclas direcionais", Symbols.action, "Calibrar"),
                lambda: self.fman.add_input(FloatingCalibrate(self.actions.settings)),
                GuiKeys.calibrate
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Criar {y} na pasta local", Symbols.action, "Rascunho"),
                self.actions.create_draft,
                GuiKeys.create_draft
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} {y} pasta de rascunhos", Symbols.action, "Reload"),
                self.actions.reload_game,
                GuiKeys.reload_game
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Ver {y} da tarefa ", Symbols.action, "versões"),
                self.actions.open_versions,
                GuiKeys.unfold_patch
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} {y} painel", Symbols.action, "Aumentar"),
                lambda: self.actions.resize_panels(10),
                GuiKeys.panel_resize_inc
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} {y} painel", Symbols.action, "Diminuir"),
                lambda: self.actions.resize_panels(-10),
                GuiKeys.panel_resize_dec
            )
        )

        self.fman.add_input(
            FloatingDropDown().set_floating(
                    Floating().top()
                    .set_text_ljust()
                    .set_footer(" Use Enter para aplicar e Esc para Sair ")
                    .set_header(" Selecione uma ação da lista ")
            )
            .set_options(options)
            .set_exit_on_enter(False)
        )