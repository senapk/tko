from tko.play.floating import FloatingInputData, FloatingInput
from tko.util.text import Text
from tko.util.symbols import symbols
from tko.play.keys import GuiKeys
from tko.play.flags import Flags
from tko.play.play_actions import PlayActions
from tko.play.floating_calibrate import FloatingCalibrate

class PlayConfig:
    def __init__(self, actions: PlayActions):
        self.actions = actions
        self.app = self.actions.settings.app
        self.fman = self.actions.fman
        self.gui = self.actions.gui

    def command_pallete(self):
        options: list[FloatingInputData] = []

        def icon(value: bool):
            return Text.Token("✓", "g") if value else Text.Token("✗", "r")
        
        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Tarefa: {y} para repositório local", symbols.action, "Baixar"),
                self.actions.down_remote_task,
                GuiKeys.down_task
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Tarefa: Abrir {y} com a descrição", symbols.action, "URL"),
                self.actions.open_link,
                GuiKeys.open_url
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Tarefa: {y} arquivos na IDE", symbols.action, "Editar"),
                self.actions.open_code,
                GuiKeys.edit
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y}", symbols.action, "Ajuda"),
                self.gui.show_help,
                GuiKeys.key_help
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y}", icon(self.app.get_use_borders()), "Bordas"),
                self.app.toggle_borders,
                GuiKeys.borders
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y}", icon(self.app.get_use_images()), "Imagens"),
                self.app.toggle_images, 
                GuiKeys.images
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mudar linguagem de download de {y}", symbols.action, "Rascunhos"),
                self.gui.language.set_language,
                GuiKeys.set_lang_drafts
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} {y} as teclas direcionais", symbols.action, "Calibrar"),
                lambda: self.fman.add_input(FloatingCalibrate(self.actions.settings)),
                GuiKeys.calibrate
            ).set_exit_on_action(True)
        )

        self.fman.add_input(
            FloatingInput(self.actions.settings, "^").set_text_ljust()
                      .set_header(" Selecione uma ação da lista ")
                      .set_options(options)
                      .set_exit_on_enter(False)
                      .set_footer(" Use Enter para aplicar e Esc para Sair ")
        )