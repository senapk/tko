from tko.floating.floating_drop_down import FloatingDropDown
from tko.floating.floating_drop_down import FloatingInputData
from tko.config.app_settings import ToggleOption
from tko.util.rt import RT
from tko.play.keys import GuiKeys
from tko.play.play_actions import PlayActions
from tko.floating.floating_calibrate import FloatingCalibrate
from tko.floating import Floating
from tko.i18n import Msg, t
from tko.util.symbols import Symbols


class _PaletteMsg:
    DOWN_TASK            = Msg(pt=" {symbol} Tarefa: [y]Baixar tarefa[] para o repositório",    en=" {symbol} Task: [y]Download task[] to repository")
    EVALUATE             = Msg(pt=" {symbol} Tarefa: [y]Avaliar tarefa[]",                      en=" {symbol} Task: [y]Evaluate task[]")
    DELETE               = Msg(pt=" {symbol} Tarefa: [y]Excluir tarefa[]",                      en=" {symbol} Task: [y]Delete task[]")
    DRAFT                = Msg(pt=" {symbol} Tarefa: [y]Criar rascunho[]",                      en=" {symbol} Task: [y]Create draft[]")
    IMAGES               = Msg(pt=" {symbol} Mostrar: [y]Imagens[] após passar nos testes",     en=" {symbol} Show: [y]Images[] after passing tests")
    TIME                 = Msg(pt=" {symbol} Mostrar: [y]Tempo[] gasto nas tarefas",            en=" {symbol} Show: [y]Time[] spent on tasks")
    VERSIONS             = Msg(pt=" {symbol} Mostrar: [y]Ver versões[] da tarefa",              en=" {symbol} Show: [y]Show task versions[]")
    LANGUAGE             = Msg(pt=" {symbol} Config: [y]Mudar <linguagem[] de programação",     en=" {symbol} Config: Change [y]programming language[]")
    UI_LANGUAGE          = Msg(pt=" {symbol} Config: [y]Alternar <idioma[] da interface PT/EN", en=" {symbol} Config: [y]Toggle UI language[] PT/EN")
    CALIBRATE            = Msg(pt=" {symbol} Config: [y]Calibrar <teclas[] do teclado",         en=" {symbol} Config: Calibrate [y]keyboard keys[]")
    RELOAD               = Msg(pt=" {symbol} Config: [y]Recarregar TKO[]",                      en=" {symbol} Config: [y]Reload TKO[]")
    INCREASE_PANEL_SIZE  = Msg(pt=" {symbol} Mostrar: [y]Aumentar[] tamanho do painel",         en=" {symbol} Show: [y]Increase[] panel size")
    DECREASE_PANEL_SIZE  = Msg(pt=" {symbol} Mostrar: [y]Diminuir[] tamanho do painel",         en=" {symbol} Show: [y]Decrease[] panel size")

class PlayPalette:
    def __init__(self, actions: PlayActions):
        self.actions = actions
        self.flags = self.actions.repo.flags
        self.app = self.actions.settings.app
        self.fman = self.actions.fman
        self.gui = self.actions.gui

    def command_pallete(self):
        def icon(value: bool) -> str:
            return "✓" if value else "✗"

        options: list[FloatingInputData] = []
                
        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.DOWN_TASK).format(Symbols.action)),
                self.actions.downloader.down_remote_task,
                GuiKeys.down_task
            ).set_exit_on_action(True)
        )

        # self evaluate
        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.EVALUATE).format(Symbols.action)),
                self.actions.evaluator.self_evaluate,
                GuiKeys.self_evaluate
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.DELETE).format(Symbols.action)),
                self.actions.delete_folder_ask,
                GuiKeys.delete_folder
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.DRAFT).format(Symbols.action)),
                self.actions.draft_creator.create_draft,
                GuiKeys.create_draft
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.LANGUAGE).format(Symbols.action)),
                self.gui.language.set_language,
                GuiKeys.set_lang_drafts
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.UI_LANGUAGE).format(Symbols.action)),
                self.gui.language.toggle_ui_language,
                GuiKeys.toggle_ui_language
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.CALIBRATE).format(Symbols.action)),
                lambda: self.fman.add_input(FloatingCalibrate(self.actions.settings)),
                GuiKeys.calibrate
            ).set_exit_on_action(True)
        )



        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.RELOAD).format(Symbols.action)),
                self.actions.reload,
                GuiKeys.reload_game
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.IMAGES).format(Symbols.action, icon(self.app.use_images))),
                lambda: self.app.toggle(ToggleOption.IMAGES),
                GuiKeys.images
            )
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.TIME).format(Symbols.action, icon(self.flags.show_time.is_true()))),
                lambda: self.flags.show_time.toggle(),
                GuiKeys.show_duration
            )
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.VERSIONS).format(symbol=Symbols.action)),
                self.actions.editor.open_versions,
                GuiKeys.unfold_patch
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.INCREASE_PANEL_SIZE).format(symbol=Symbols.action)),
                lambda: self.actions.resize_panels(10),
                GuiKeys.panel_resize_inc
            )
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.DECREASE_PANEL_SIZE).format(symbol=Symbols.action)),
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
