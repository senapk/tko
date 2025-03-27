from tko.play.floating import FloatingInputData, FloatingInput
from tko.util.text import Text, Token
from tko.util.symbols import symbols
from tko.play.keys import GuiKeys
from tko.play.flags import Flags
from tko.play.play_actions import PlayActions
from tko.play.floating_manager import FloatingManager

class PlayPalette:
    def __init__(self, actions: PlayActions):
        self.actions = actions
        self.app = self.actions.settings.app
        self.fman = self.actions.fman
        self.gui = self.actions.gui

    def command_pallete(self):
        options: list[FloatingInputData] = []

        def icon(value: bool):
            return Token("✓", "g") if value else Token("✗", "r")
        
        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Tarefa: {y} para repositório local", symbols.action, "Baixar"),
                self.actions.down_remote_task,
                GuiKeys.down_task
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Tarefa: Abrir {y} com a descrição", symbols.action, "GitHub"),
                self.actions.open_link,
                GuiKeys.github_web
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
                lambda: Text.format(" {} Mostrar atividades {y}", icon(self.app.get_show_hidden()), "Escondidas"),
                self.app.toggle_hidden, 
                GuiKeys.hidden
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y}", icon(Flags.percent), "Percentual"),
                Flags.percent.toggle, 
                Flags.percent.get_keycode()
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y} para completar a missão", icon(Flags.minimum), "Mínimo"),
                Flags.minimum.toggle,
                Flags.minimum.get_keycode()
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y} das tarefas", icon(Flags.reward), "Recompensa"),
                Flags.reward.toggle, 
                Flags.reward.get_keycode()
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mostrar {y}", icon(Flags.skills), "Skills"),
                Flags.skills.toggle, 
                Flags.skills.get_keycode()
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Modo {y}: Habilitar todas as tarefas", icon(Flags.admin), "Admin"),
                Flags.admin.toggle,
                Flags.admin.get_keycode()
            )
        )

        # options.append(
        #     FloatingInputData(
        #         lambda: Text.format(" {} Gerar {y} de dependências", symbols.action, "Grafo"),
        #         self.actions.generate_graph,
        #         GuiKeys.graph
        #     ).set_exit_on_action(True)
        # )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Mudar {y} de download de rascunhos", symbols.action, "Linguagem"),
                self.gui.language.set_language,
                GuiKeys.set_lang
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Devel: Habilita mensagens de {y}", icon(Flags.devel), "Debug"),
                Flags.devel.toggle,
                ""
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Muda o gráfico {y}", icon(Flags.graph), "Graph"),
                Flags.graph.toggle,
                Flags.graph.get_keycode()
            )
        )

        options.append(
            FloatingInputData(
                lambda: Text.format(" {} Devel: Marcar em {y}", symbols.action, "Massa"),
                self.gui.tree.mass_mark,
                ""
            ).set_exit_on_action(True)
        )

        self.fman.add_input(
            FloatingInput("^").set_text_ljust()
                      .set_header(" Selecione uma ação da lista ")
                      .set_options(options)
                      .set_exit_on_enter(False)
                      .set_footer(" Use Enter para aplicar e Esc para Sair ")
        )