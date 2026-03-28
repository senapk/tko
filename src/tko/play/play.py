from tko.game.game import Game
from tko.play.fmt import Fmt
from tko.play.language_setter import LanguageSetter
from tko.settings.settings import Settings
from tko.settings.repository import Repository
from tko.play.keys import GuiKeys
from tko.play.images import opening
from tko.play.floating_calibrate import FloatingCalibrate
from tko.play.input_manager import InputManager
from tko.play.play_palette import PlayPalette
from tko.play.floating import Floating
from tko.play.floating_manager import FloatingManager
from tko.play.flags import Flags, FlagsMan
from tko.play.tasktree import TaskTree
from tko.play.gui import Gui
from tko.play.play_actions import PlayActions
from tko.play.flag_functors import FlagFunctor
from icecream import ic # type: ignore

import curses

class Play:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.app = settings.app
        self.repo = repo
        self.game: Game = repo.game
        self.exit = False

        self.flagsman = FlagsMan(self.repo.data.flags)
        self.fman = FloatingManager()
        self.tree = TaskTree(self.settings, repo, self.fman)
        self.gui = Gui(settings=self.settings, tree=self.tree, flagsman=self.flagsman, fman=self.fman)
        self.actions = PlayActions(self.gui)
        self.play_palette = PlayPalette(self.actions)
        # self.fman.add_input( Floating().set_content(opening['yoda'].splitlines()).set_warning() )

    def display_need_update(self):
        self.gui.set_need_update()

    def save_to_json(self):
        self.tree.save_on_rep()
        self.repo.data.flags = self.flagsman.get_data()
        self.settings.save_settings()
        self.repo.save_config()

    def send_quit_msg(self):
        def set_exit():
            self.exit = True

        self.fman.add_input(
            Floating().set_content(opening['cool'].splitlines()).set_exit_fn(set_exit).set_exit_key('q').set_warning()
        )

    def move_up(self):
        self.tree.move_up()
        self.gui.xray_offset = 0

    def move_down(self):
        self.tree.move_down()
        self.gui.xray_offset = 0

    def page_up(self):
        if Flags.panel.get_value() == Flags.panel_logs:
            self.gui.xray_offset -= 5
        elif Flags.panel.get_value() == Flags.panel_graph:
            Flags.task_graph_mode.set_value(Flags.task_exec_view)
    
    def page_down(self):
        if Flags.panel.get_value() == Flags.panel_logs:
            self.gui.xray_offset += 5
        elif Flags.panel.get_value() == Flags.panel_graph:
            Flags.task_graph_mode.set_value(Flags.task_time_view)


    def move_left(self):
        self.gui.xray_offset = 0
        self.tree.arrow_left()

    def move_right(self):
        self.gui.xray_offset = 0
        self.tree.arrow_right()

    def activate(self):
        self.gui.xray_offset = 0
        return self.actions.select_task()

    def make_callback(self) -> InputManager:
        cman = InputManager()

        cman.add_str(GuiKeys.key_quit, self.send_quit_msg)
        cman.add_int(curses.KEY_EXIT, self.send_quit_msg)
        cman.add_int(curses.KEY_UP, self.move_up)
        cman.add_int(curses.KEY_DOWN, self.move_down)
        cman.add_int(curses.KEY_LEFT, self.move_left)
        cman.add_int(curses.KEY_RIGHT, self.move_right)
        cman.add_str(GuiKeys.reload_game, self.actions.reload_game)

        cman.add_int(curses.KEY_NPAGE, self.page_down)
        cman.add_int(curses.KEY_PPAGE, self.page_up)

        cman.add_str(GuiKeys.calibrate, lambda: self.fman.add_input(FloatingCalibrate(self.settings)))
        cman.add_str(GuiKeys.activate, self.activate) # type: ignore
        # cman.add_str(GuiKeys.open_url, self.actions.open_link)
        cman.add_str(GuiKeys.down_task, self.actions.down_remote_task)
        cman.add_str(GuiKeys.borders, lambda: self.app.toggle("use_borders"))
        cman.add_str(GuiKeys.images, lambda: self.app.toggle("use_images"))
        cman.add_str(GuiKeys.set_lang_drafts, self.gui.language.set_language)
        cman.add_str(GuiKeys.create_draft, self.actions.create_draft)
        cman.add_int(curses.KEY_DC, self.actions.delete_folder_ask)
        cman.add_str(GuiKeys.delete_folder, self.actions.delete_folder_ask)

        cman.add_str(GuiKeys.self_evaluate, self.actions.self_evaluate)
        if ic.enabled:
            cman.add_str(GuiKeys.self_evaluate_full, self.actions.self_evaluate_full)
        cman.add_str(GuiKeys.inbox, lambda: Flags.inbox.set_value(Flags.inbox_only))
        cman.add_str(GuiKeys.all_tasks, lambda: Flags.inbox.set_value(Flags.inbox_all))

        cman.add_str(GuiKeys.panel_help, lambda: self.open_panel(Flags.panel_help))
        cman.add_str(GuiKeys.panel_graph, lambda: self.open_panel(Flags.panel_graph))
        cman.add_str(GuiKeys.panel_logs, lambda: self.open_panel(Flags.panel_logs))
        cman.add_str(GuiKeys.panel_skills, lambda: self.open_panel(Flags.panel_skills))
        cman.add_str(GuiKeys.panel_toggle, lambda: Flags.show_panel.toggle())

        cman.add_str(GuiKeys.unfold_patch, self.actions.open_versions)
        
        for flag in self.flagsman.flags.values():
            if flag.get_autoload():
                cman.add_str(flag.get_keycode(), FlagFunctor(flag, self.fman))

        cman.add_str(GuiKeys.search, self.gui.search.toggle_search)
        cman.add_str(GuiKeys.palette, self.play_palette.command_pallete)
        cman.add_str(GuiKeys.panel_resize_inc, lambda: self.actions.resize_panels(10))
        cman.add_str(GuiKeys.panel_resize_dec, lambda: self.actions.resize_panels(-10))

        return cman

    def open_panel(self, value: str):
        if Flags.show_panel.is_true():
            if Flags.panel.get_value() != value:
                Flags.panel.set_value(value)
            else:
                Flags.show_panel.set_value("0")
            return
        Flags.show_panel.set_value("1")
        if Flags.panel.get_value() != value:
            Flags.panel.set_value(value)

    def open_help(self):
        if not Flags.show_panel.is_true():
            Flags.show_panel.set_value("1")
            Flags.panel.set_value(Flags.panel_help)
        elif Flags.panel.get_value() != Flags.panel_help:
            Flags.panel.set_value(Flags.panel_help)

    def send_char_not_found(self, key: int):
        exclude_str = [ord(v) for v in [" ", "\n"]]
        exclude_int = [ -1, curses.KEY_EXIT, curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_BACKSPACE]
        if key in exclude_int + exclude_str:
            return
        if key < 0 or key > 255:
            return
        self.fman.add_input( Floating().bottom().right().set_error().put_text(f"Tecla char:{chr(key)}, code:{key}, não reconhecida") )


    def main(self, scr: curses.window):
        InputManager.fix_esc_delay()
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global

        while True:
            self.tree.update_tree(admin_mode=Flags.inbox.get_value() == Flags.inbox_all or self.gui.search.search_mode)
            self.fman.draw_warnings()
            cman = self.make_callback()
            self.gui.show_items()

            if self.fman.has_floating():
                self.fman.draw()

            # o input tem que ser depois do draw para mostrar o floating
            value = InputManager.get_and_remap_keys(scr, self.app)
            
            if self.fman.has_floating():
                # if consumed, value becomes -1
                value = self.fman.process_input(value)
                
            if self.exit:
                break

            if self.gui.search.search_mode:
                self.gui.search.process_search(value)
            elif cman.has_int_key(value):
                callback = cman.exec_call(value)
                if callback is not None:
                    return callback
            else:
                self.send_char_not_found(value)

            self.tree.reload_sentences()
            self.save_to_json()
            
    def play(self):
        LanguageSetter.check_lang_in_text_mode(self.settings, self.repo)

        while True:
            output = curses.wrapper(self.main)
            if output is None:
                return
            else:
                output()
