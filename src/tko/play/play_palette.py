from tko.floating.floating_drop_down import FloatingDropDown
from tko.floating.floating_drop_down import FloatingInputData
from tko.config.app_settings import ToggleOption
from tko.util.rtext import RText
from tko.util.symbols import Symbols
from tko.play.keys import GuiKeys
from tko.play.play_actions import PlayActions
from tko.floating.floating_calibrate import FloatingCalibrate
from tko.floating import Floating
from tko.i18n import MsgKey, t

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
            return RText("✓", "g") if value else RText("✗", "r")
        
        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] Tarefa: [y][][.] para o repositório", Symbols.action, t(MsgKey.PLAY_PALETTE_DOWN_TASK)),
                self.actions.downloader.down_remote_task,
                GuiKeys.down_task
            ).set_exit_on_action(True)
        )

        # self evaluate
        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] Tarefa: Auto [y][][.] método de estudo", Symbols.action, t(MsgKey.PLAY_PALETTE_EVALUATE)),
                self.actions.evaluator.self_evaluate,
                GuiKeys.self_evaluate
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] Tarefa: [y][][.] pasta", Symbols.action, t(MsgKey.PLAY_PALETTE_DELETE)),
                self.actions.delete_folder_ask,
                GuiKeys.delete_folder
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] {t(MsgKey.PLAY_PALETTE_HELP)} [y][][.]", Symbols.action, "Ajuda"),
                lambda: self.flags.panel.set_help(),
                GuiKeys.panel_help
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] {t(MsgKey.PLAY_PALETTE_BORDERS)} [y][][.]", icon(self.app.use_borders), "Bordas"),
                lambda: self.app.toggle(ToggleOption.BORDERS),
                GuiKeys.borders
            )
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] {t(MsgKey.PLAY_PALETTE_IMAGES)} [y][][.]", icon(self.app.use_images), "Imagens"),
                lambda: self.app.toggle(ToggleOption.IMAGES),
                GuiKeys.images
            )
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] {t(MsgKey.PLAY_PALETTE_TIME)} [y][][.] decorrido", icon(self.flags.show_time.is_true()), "Tempo"),
                lambda: self.flags.show_time.toggle(),
                GuiKeys.show_duration
            )
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] {t(MsgKey.PLAY_PALETTE_LANGUAGE)} [y][][.] de programação", Symbols.action, "Línguagem"),
                self.gui.language.set_language,
                GuiKeys.set_lang_drafts
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] {t(MsgKey('play.palette.ui_language'))} [y][][.] PT/EN", Symbols.action, "Interface"),
                self.gui.language.toggle_ui_language,
                GuiKeys.toggle_ui_language
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] {t(MsgKey.PLAY_PALETTE_CALIBRATE)} [y][][.] as teclas direcionais", Symbols.action, "Calibrar"),
                lambda: self.fman.add_input(FloatingCalibrate(self.actions.settings)),
                GuiKeys.calibrate
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] {t(MsgKey.PLAY_PALETTE_DRAFT)} [y][][.] na pasta local", Symbols.action, "Rascunho"),
                self.actions.draft_creator.create_draft,
                GuiKeys.create_draft
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] {t(MsgKey.PLAY_PALETTE_RELOAD)} [y][][.] pasta de rascunhos", Symbols.action, "Reload"),
                self.actions.reload,
                GuiKeys.reload_game
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] {t(MsgKey.PLAY_PALETTE_VERSIONS)} [y][][.] da tarefa ", Symbols.action, "versões"),
                self.actions.editor.open_versions,
                GuiKeys.unfold_patch
            ).set_exit_on_action(True)
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] [y][][.] {t(MsgKey.PLAY_PALETTE_PANEL_SIZE)}", Symbols.action, "Aumentar"),
                lambda: self.actions.resize_panels(10),
                GuiKeys.panel_resize_inc
            )
        )

        options.append(
            FloatingInputData(
                lambda: RText.parse(f" [] [y][][.] {t(MsgKey.PLAY_PALETTE_PANEL_SIZE)}", Symbols.action, "Diminuir"),
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
