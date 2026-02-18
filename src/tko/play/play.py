from tko.game.game import Game
from tko.play.fmt import Fmt
from tko.settings.languages import available_languages
from tko.settings.settings import Settings
from tko.settings.repository import Repository
from tko.play.keys import GuiKeys
from tko.play.images import opening
from tko.play.floating_calibrate import FloatingCalibrate
from tko.play.input_manager import InputManager
from tko.play.play_pallete import PlayConfig
from tko.play.floating import Floating
from tko.play.floating_manager import FloatingManager
from tko.play.flags import Flags, FlagsMan
from tko.play.tasktree import TaskTree
from tko.play.gui import Gui
from tko.play.play_actions import PlayActions
from tko.play.flag_functors import FlagFunctor

import curses

class Play:
    def __init__(self, settings: Settings, rep: Repository):
        self.settings = settings
        self.app = settings.app
        self.rep = rep
        self.game: Game = rep.game
        self.exit = False

        self.flagsman = FlagsMan(self.rep.data.flags)
        self.fman = FloatingManager()
        self.tree = TaskTree(self.settings, rep, self.fman)
        self.gui = Gui(tree=self.tree, flagsman=self.flagsman, fman=self.fman)
        self.actions = PlayActions(self.gui)
        self.play_palette = PlayConfig(self.actions)
        self.fman.add_input(
            Floating(self.settings).set_content(opening['yoda'].splitlines()).set_warning()
        )

    def set_need_update(self):
        self.gui.set_need_update()

    def save_to_json(self):
        self.tree.save_on_rep()
        self.rep.data.flags = self.flagsman.get_data()
        self.settings.save_settings()
        self.rep.save_config()

    def send_quit_msg(self):
        def set_exit():
            self.exit = True

        self.fman.add_input(
            Floating(self.settings).set_content(opening['cool'].splitlines()).set_exit_fn(set_exit).set_exit_key('q').set_warning()
        )

    def move_up(self):
        self.tree.move_up()
        self.gui.xray_offset = 0

    def move_down(self):
        self.tree.move_down()
        self.gui.xray_offset = 0

    def page_up(self):
        if Flags.graph.get_value() == Flags.graph_logs:
            self.gui.xray_offset -= 5
        elif Flags.graph.get_value() == Flags.graph_task:
            Flags.task_graph.set_value(Flags.task_exec_view)
    
    def page_down(self):
        if Flags.graph.get_value() == Flags.graph_logs:
            self.gui.xray_offset += 5
        elif Flags.graph.get_value() == Flags.graph_task:
            Flags.task_graph.set_value(Flags.task_time_view)


    def move_left(self):
        self.gui.xray_offset = 0
        self.tree.arrow_left()

    def move_right(self):
        self.gui.xray_offset = 0
        self.tree.arrow_right()

    def activate(self):
        self.gui.xray_offset = 0
        return self.actions.select_task()

    def reload_sources(self):
        self.game.reload_sources()

    def make_callback(self) -> InputManager:
        cman = InputManager()

        cman.add_str(GuiKeys.key_quit, self.send_quit_msg)
        cman.add_int(curses.KEY_EXIT, self.send_quit_msg)
        cman.add_int(curses.KEY_UP, self.move_up)
        cman.add_int(curses.KEY_DOWN, self.move_down)
        cman.add_int(curses.KEY_LEFT, self.move_left)
        cman.add_int(curses.KEY_RIGHT, self.move_right)
        cman.add_str(GuiKeys.reload_sources, self.reload_sources)

        cman.add_int(curses.KEY_NPAGE, self.page_down)
        cman.add_int(curses.KEY_PPAGE, self.page_up)

        cman.add_str(GuiKeys.calibrate, lambda: self.fman.add_input(FloatingCalibrate(self.settings)))
        cman.add_str(GuiKeys.activate, self.activate) # type: ignore
        cman.add_str(GuiKeys.open_url, self.actions.open_link)
        cman.add_str(GuiKeys.down_task, self.actions.down_remote_task)
        cman.add_str(GuiKeys.borders, self.app.toggle_borders)
        cman.add_str(GuiKeys.images, self.app.toggle_images)
        cman.add_str(GuiKeys.set_lang_drafts, self.gui.language.set_language)
        cman.add_str(GuiKeys.create_draft, self.actions.create_draft)

        cman.add_str(GuiKeys.grade_play, self.actions.self_evaluate)
        cman.add_int(curses.KEY_BACKSPACE, self.actions.self_evaluate)
        
        cman.add_str(GuiKeys.key_help, self.gui.show_help)
        cman.add_str(GuiKeys.unfold_patch, self.actions.open_versions)
        
        for flag in self.flagsman.flags.values():
            if flag.get_autoload():
                cman.add_str(flag.get_keycode(), FlagFunctor(flag, self.fman, self.settings))

        cman.add_str(GuiKeys.search, self.gui.search.toggle_search)
        cman.add_str(GuiKeys.palette, self.play_palette.command_pallete)

        return cman
        

    def send_char_not_found(self, key: int):
        exclude_str = [ord(v) for v in [" ", "a", "d", "\n"]]
        exclude_int = [ -1, curses.KEY_EXIT, curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_BACKSPACE]
        if key in exclude_int + exclude_str:
            return
        if key < 0 or key > 255:
            return
        self.fman.add_input( Floating(self.settings, "v>").set_error().put_text(f"Tecla char:{chr(key)}, code:{key}, não reconhecida") )


    def main(self, scr: curses.window):
        InputManager.fix_esc_delay()
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global

        while True:
            self.tree.update_tree(admin_mode=Flags.quests.get_value() == "2" or self.gui.search.search_mode)
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

    def check_lang_in_text_mode(self):
        lang = self.rep.data.lang
        if lang == "":
            options = available_languages
            print("\nLinguagem padrão ainda não foi definida.\n")
            while True:
                print("Escolha entre as opções a seguir ", end="")
                print("[" + ", ".join(options) + "]", ":", end=" ")
                lang = input()
                if lang in options:
                    break
            self.rep.data.lang = lang


    def play(self):
        self.check_lang_in_text_mode()

        while True:
            output = curses.wrapper(self.main)
            if output is None:
                return
            else:
                output()
