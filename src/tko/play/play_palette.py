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
    DOWN_TASK            = Msg(pt=" <$> Tarefa: [y]Baixar tarefa[.] para o repositório",   en=" <$> Task: [y]Download task[.] to repository")
    EVALUATE             = Msg(pt=" <$> Tarefa: [y]Avaliar tarefa[.]",                     en=" <$> Task: [y]Evaluate task[.]")
    DELETE               = Msg(pt=" <$> Tarefa: [y]Excluir tarefa[.]",                     en=" <$> Task: [y]Delete task[.]")
    DRAFT                = Msg(pt=" <$> Tarefa: [y]Criar rascunho[.]",                     en=" <$> Task: [y]Create draft[.]")
    IMAGES               = Msg(pt=" <$> Mostrar: [y]Imagens[.] após passar nos testes",    en=" <$> Show: [y]Images[.] after passing tests")
    TIME                 = Msg(pt=" <$> Mostrar: [y]Tempo[.] gasto nas tarefas",           en=" <$> Show: [y]Time[.] spent on tasks")
    VERSIONS             = Msg(pt=" <$> Mostrar: [y]Ver versões[.] da tarefa",             en=" <$> Show: [y]Show task versions[.]")
    LANGUAGE             = Msg(pt=" <$> Config: Mudar [y]linguagem[.] de programação",     en=" <$> Config: Change [y]programming language[.]")
    UI_LANGUAGE          = Msg(pt=" <$> Config: Alternar [y]idioma[.] da interface PT/EN", en=" <$> Config: [y]Toggle UI language[.] PT/EN")
    CALIBRATE            = Msg(pt=" <$> Config: Calibrar [y]teclas[.] do teclado",         en=" <$> Config: Calibrate [y]keyboard keys[.]")
    RELOAD               = Msg(pt=" <$> Config: [y]Recarregar TKO[.]",                     en=" <$> Config: [y]Reload TKO[.]")
    INCREASE_PANEL_SIZE  = Msg(pt=" <$> Mostrar: [y]Aumentar[.] tamanho do painel",        en=" <$> Show: [y]Increase[.] panel size")
    DECREASE_PANEL_SIZE  = Msg(pt=" <$> Mostrar: [y]Diminuir[.] tamanho do painel",        en=" <$> Show: [y]Decrease[.] panel size")

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
                lambda: RT.parse(t(_PaletteMsg.DOWN_TASK), Symbols.action,),
                self.actions.downloader.down_remote_task,
                GuiKeys.down_task
            ).set_exit_on_action(True)
        )

        # self evaluate
        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.EVALUATE), Symbols.action,),
                self.actions.evaluator.self_evaluate,
                GuiKeys.self_evaluate
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.DELETE), Symbols.action,),
                self.actions.delete_folder_ask,
                GuiKeys.delete_folder
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.DRAFT), Symbols.action,),
                self.actions.draft_creator.create_draft,
                GuiKeys.create_draft
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.LANGUAGE), Symbols.action,),
                self.gui.language.set_language,
                GuiKeys.set_lang_drafts
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.UI_LANGUAGE), Symbols.action,),
                self.gui.language.toggle_ui_language,
                GuiKeys.toggle_ui_language
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.CALIBRATE), Symbols.action,),
                lambda: self.fman.add_input(FloatingCalibrate(self.actions.settings)),
                GuiKeys.calibrate
            ).set_exit_on_action(True)
        )



        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.RELOAD), Symbols.action,),
                self.actions.reload,
                GuiKeys.reload_game
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.IMAGES), icon(self.app.use_images),),
                lambda: self.app.toggle(ToggleOption.IMAGES),
                GuiKeys.images
            )
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.TIME), icon(self.flags.show_time.is_true()),),
                lambda: self.flags.show_time.toggle(),
                GuiKeys.show_duration
            )
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.VERSIONS), Symbols.action,),
                self.actions.editor.open_versions,
                GuiKeys.unfold_patch
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.INCREASE_PANEL_SIZE), Symbols.action,),
                lambda: self.actions.resize_panels(10),
                GuiKeys.panel_resize_inc
            )
        )

        options.append(
            FloatingInputData(
                lambda: RT.parse(t(_PaletteMsg.DECREASE_PANEL_SIZE), Symbols.action,),
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
