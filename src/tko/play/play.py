from tko.game.game import Game
from tko.repository.repository_watcher import RepositoryWatcher
from tko.widget.fmt import Fmt
from tko.play.language_setter import LanguageSetter
from tko.config.app_settings import ToggleOption
from tko.repository.repository_config import RepositoryConfig
from tko.config.settings import Settings
from tko.repository.repository import Repository
from tko.play.gui_keys import GuiKeys
from tko.floating.floating_calibrate import FloatingCalibrate
from tko.floating.floating import AlignX, Floating, AlignY, Position
from tko.floating.floating_manager import FloatingManager, FloatingWriter
from tko.play.input_manager import InputManager
from tko.play.play_palette import PlayPalette
from tko.floating.floating_manager import FloatingManager, FloatingWriter
from tko.util.console import Console
from tko.play_tree.task_tree import TaskTree
from tko.play_gui.gui import Gui
from tko.play.play_actions import PlayActions
from tko.play.flag_functors import FlagFunctor
from tko.play_gui.gui_help_info import GuiHelpInfo
from tko.i18n import Msg
from icecream import ic # type: ignore
from tko.widget.fmt import Fmt

import curses


_PLAY_KEY_NOT_RECOGNIZED = Msg.text(
    pt="Tecla char:{char}, code:{code}, não reconhecida",
    en="Key char:{char}, code:{code}, not recognized",
)

class Play:
    def __init__(self, settings: Settings, repo: Repository, watcher: RepositoryWatcher | None):
        self.settings = settings
        self.app = settings.app
        self.repo = repo
        self.watcher = watcher
        self.game: Game = repo.game
        self.exit = False
        self.flags = repo.flags
        self.fman: FloatingManager = FloatingManager()        
        self.tree = TaskTree(self.settings, repo) # type: ignore
        self.gui = Gui(tree=self.tree, fman=self.fman, watcher=self.watcher)
        self.actions = PlayActions(self.gui)
        self.play_palette = PlayPalette(self.actions)
        self.loader = RepositoryConfig(repo)

    def get_left_frame_size(self) -> int:
        _, cols = Fmt.get_lines_cols()
        left_width = int(cols * self.settings.app.panel_size_percent / 100)
        return left_width

    def display_need_update(self):
        self.gui.set_need_update()

    def show_help(self):
        self.fman.add_floating(
            Floating().set_content_rt(GuiHelpInfo.show()).set_header(f" {Msg.text(pt="Ajuda", en="Help")} ").set_countdown(100)
        )

    def save_to_json(self):
        self.tree.save_state()
        self.settings.save_settings()
        self.loader.save(force=self.exit)

    def quit_now(self):
        self.exit = True

    def move_up(self):
        self.tree.move_up()
        self.gui.xray_offset = 0

    def move_down(self):
        self.tree.move_down()
        self.gui.xray_offset = 0

    def page_up(self):
        if self.flags.panel.is_logs():
            self.gui.xray_offset -= 5
        elif self.flags.panel.is_graph():
            self.flags.task_graph_mode.set_exec_view()
    
    def page_down(self):
        if self.flags.panel.is_logs():
            self.gui.xray_offset += 5
        elif self.flags.panel.is_graph():
            self.flags.task_graph_mode.set_time_view()


    def move_left(self):
        self.gui.xray_offset = 0
        self.tree.move_left()

    def move_right(self):
        self.gui.xray_offset = 0
        self.tree.move_right()

    def activate(self):
        self.gui.xray_offset = 0
        return self.actions.launcher.select_task()

    def exit_step(self):
        self.exit = True

    def make_callback(self) -> InputManager:
        cman = InputManager()

        cman.add_str(GuiKeys.key_quit, self.quit_now)
        cman.add_int(curses.KEY_EXIT, self.exit_step)
        cman.add_int(curses.KEY_UP, self.move_up)
        cman.add_int(curses.KEY_DOWN, self.move_down)
        cman.add_int(curses.KEY_LEFT, self.move_left)
        cman.add_int(curses.KEY_RIGHT, self.move_right)
        cman.add_str(GuiKeys.reload_game, self.actions.reload)

        cman.add_int(curses.KEY_NPAGE, self.page_down)
        cman.add_int(curses.KEY_PPAGE, self.page_up)

        cman.add_str(GuiKeys.calibrate, lambda: self.fman.add_floating(FloatingCalibrate(self.settings)))
        cman.add_str(GuiKeys.activate, self.activate) # type: ignore
        # cman.add_str(GuiKeys.open_url, self.actions.open_link)
        cman.add_str(GuiKeys.down_task, self.actions.downloader.down_remote_task)
        cman.add_str(GuiKeys.images, lambda: self.app.toggle(ToggleOption.IMAGES))
        cman.add_str(GuiKeys.set_lang_drafts, self.gui.language.set_language)
        cman.add_str(GuiKeys.toggle_ui_language, self.gui.language.toggle_ui_language)
        cman.add_str(GuiKeys.create_draft, self.actions.draft_creator.create_draft)
        cman.add_int(curses.KEY_DC, self.actions.delete_folder_ask)
        cman.add_str(GuiKeys.delete_folder, self.actions.delete_folder_ask)
        cman.add_str(GuiKeys.expand_all, self.tree.expand_all)
        cman.add_str(GuiKeys.collapse_all, self.tree.collapse_all)

        cman.add_str(GuiKeys.self_evaluate, self.actions.evaluator.self_evaluate)
        if ic.enabled:
            cman.add_str(GuiKeys.self_evaluate_full, self.actions.evaluator.self_evaluate_full)
        cman.add_str(GuiKeys.inbox, lambda: self.flags.task_view_mode.set_view_inbox())
        cman.add_str(GuiKeys.all_tasks, lambda: self.flags.task_view_mode.set_view_all())

        cman.add_str(GuiKeys.ask_help, self.show_help)
        cman.add_str(GuiKeys.panel_graph, lambda: self.open_toggle_panel(self.flags.panel.GRAPH))
        cman.add_str(GuiKeys.panel_logs, lambda: self.open_toggle_panel(self.flags.panel.LOGS))
        cman.add_str(GuiKeys.panel_skills, lambda: self.open_toggle_panel(self.flags.panel.SKILLS))

        cman.add_str(GuiKeys.unfold_patch, self.actions.editor.open_versions)
        
        for flag in self.flags.all_flags:
            if flag.keycode:
                cman.add_str(flag.keycode, FlagFunctor(flag, self.fman))

        cman.add_str(GuiKeys.search, self.gui.search.toggle_search)
        cman.add_str(GuiKeys.palette, self.play_palette.command_pallete)
        cman.add_str(GuiKeys.panel_resize_inc, lambda: self.actions.resize_panels(5))
        cman.add_str(GuiKeys.panel_resize_dec, lambda: self.actions.resize_panels(-5))
 

        return cman

    def open_toggle_panel(self, value: str):
        current = self.flags.panel.get_value()
        panel = self.flags.panel        
        if current != value:
            panel.set_value(value)
        return

    def send_char_not_found(self, key: int):
        exclude_str = [ord(v) for v in [" ", "\n"]]
        exclude_int = [ -1, curses.KEY_EXIT, curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_BACKSPACE]
        if key in exclude_int + exclude_str:
            return
        if key < 0 or key > 255:
            return
        self.fman.add_floating(
            Floating().bottom().right().set_error().put_text(
                str(_PLAY_KEY_NOT_RECOGNIZED).format(char=chr(key), code=key)
            ).set_countdown(Floating.Time.FAST)
        )


    def main(self, scr: curses.window):
        InputManager.fix_esc_delay()
        try:
            curses.curs_set(0)  # Esconde o cursor
        except curses.error:
            pass
        scr.keypad(True)
        Fmt.set_scr(scr)  # Define o scr como global e inicializa as cores
        self.tree.layout.get_tree_size_fn = lambda: self.get_left_frame_size()
        try:
            while not self.exit:
                self.tree.update()

                self.fman.draw_floatings()
                cman = self.make_callback()

                self.gui.show_items()

                if self.fman.has_floatings():
                    self.fman.draw()

                # o input tem que ser depois do draw para mostrar o floating
                value = InputManager.get_and_remap_keys(scr, self.app)
                
                if self.fman.has_floatings():
                    # if consumed, value becomes -1
                    value = self.fman.process_input(value)
                    
                if self.gui.search.search_mode:
                    self.gui.search.process_search(value)
                elif cman.has_int_key(value):
                    callback = cman.exec_call(value)
                    if callback is not None:
                        return callback
                else:
                    self.send_char_not_found(value)
                if value != -1:
                    self.save_to_json()
        finally:
            scr.keypad(False)
            try:
                curses.curs_set(1)
            except curses.error:
                pass

            
    def play(self):
        LanguageSetter.check_prog_lang_in_text_mode(self.settings, self.repo)

        while True:
            writer = FloatingWriter(self.fman, Position(AlignY.bottom, AlignX.right, offset_x=-2, offset_y=-2))
            # with open("play.log", "a", encoding="utf-8") as f:
            #     writer = PrintWriter(f)
            with Console.redirect(stdout = writer, stderr = writer):
                output = curses.wrapper(self.main)
            if output is None:
                return
            else:
                output()
