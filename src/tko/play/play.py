from tko.game.game import Game
from tko.settings.languages import available_languages
from tko.settings.settings import Settings
from tko.settings.repository import Repository
from tko.play.keys import GuiKeys
from tko.play.floating_calibrate import FloatingCalibrate
from tko.play.fmt import Fmt
from tko.play.input_manager import InputManager
from tko.play.play_config import PlayConfig
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

        self.flagsman = FlagsMan(self.rep.get_flags())
        self.fman = FloatingManager()
        self.tree = TaskTree(self.settings, rep, self.fman)
        self.gui = Gui(tree=self.tree, flagsman=self.flagsman, fman=self.fman)

        # if len(self.rep.get_tasks()) == 0:
        #     self.gui.show_help()

        self.first_loop = True
        self.graph_ext = ""

        self.actions = PlayActions(self.gui)
        self.play_palette = PlayConfig(self.actions)

    def set_need_update(self):
        self.gui.set_need_update()

    def save_to_json(self):
        self.tree.save_on_rep()
        self.rep.set_flags(self.flagsman.get_data())
        self.settings.save_settings()
        self.rep.save_config()

    def send_quit_msg(self):
        def set_exit():
            self.exit = True

        self.fman.add_input(
            Floating(self.settings).put_text("\nAté a próxima\n").set_exit_fn(set_exit).warning()
        )

    def make_callback(self) -> InputManager:
        cman = InputManager()

        cman.add_str(GuiKeys.key_quit, self.send_quit_msg)
        cman.add_int(InputManager.esc, self.send_quit_msg)
        # cman.add_int(curses.KEY_BACKSPACE, self.send_quit_msg)

        cman.add_str(GuiKeys.up, self.tree.move_up)
        cman.add_str(GuiKeys.up2, self.tree.move_up)
        key_up = self.app.get_key_up()
        if key_up != 0:
            cman.add_int(key_up, self.tree.move_up)

        cman.add_str(GuiKeys.down, self.tree.move_down)
        cman.add_str(GuiKeys.down2, self.tree.move_down)
        key_down = self.app.get_key_down()
        if key_down != 0:
            cman.add_int(key_down, self.tree.move_down)

        cman.add_str(GuiKeys.left, self.tree.arrow_left)
        cman.add_str(GuiKeys.left2, self.tree.arrow_left)
        key_left = self.app.get_key_left()
        if key_left != 0:
            cman.add_int(key_left, self.tree.arrow_left)

        cman.add_str(GuiKeys.right, self.tree.arrow_right)
        cman.add_str(GuiKeys.right2, self.tree.arrow_right)
        key_right = self.app.get_key_right()
        if key_right != 0:
            cman.add_int(key_right, self.tree.arrow_right)

        cman.add_str(GuiKeys.calibrate, lambda: self.fman.add_input(FloatingCalibrate(self.settings)))
        
        cman.add_str(GuiKeys.activate, lambda: self.actions.select_task()) # type: ignore
        cman.add_str(GuiKeys.open_url, self.actions.open_link)
        cman.add_str(GuiKeys.down_task, self.actions.down_remote_task)
        cman.add_str(GuiKeys.edit, lambda: self.actions.open_code())
        cman.add_str(GuiKeys.expand, self.tree.process_expand_all)
        cman.add_str(GuiKeys.collapse, self.tree.process_collapse_all)
        cman.add_str(GuiKeys.borders, self.app.toggle_borders)
        cman.add_str(GuiKeys.images, self.app.toggle_images)
        cman.add_str(GuiKeys.hidden, self.app.toggle_hidden)
        cman.add_str(GuiKeys.set_lang_drafts, self.gui.language.set_language)
        cman.add_int(curses.KEY_BACKSPACE, self.actions.evaluate)
        cman.add_str(GuiKeys.grade_play, self.actions.evaluate)
    
        cman.add_str(GuiKeys.key_help, self.gui.show_help)
        
        for flag in self.flagsman.flags.values():
            cman.add_str(flag.get_keycode(), FlagFunctor(flag))

        cman.add_str(GuiKeys.search, self.gui.search.toggle_search)
        cman.add_str(GuiKeys.palette, self.play_palette.command_pallete)

        return cman
        
    def send_char_not_found(self, key: int):
        exclude_str = [ord(v) for v in [" ", "a", "d", "\n", GuiKeys.up, GuiKeys.down, GuiKeys.left, GuiKeys.right]]
        exclude_int = [ -1, InputManager.esc] + InputManager.backspace_list
        if key in exclude_int + exclude_str:
            return
        if key < 0 or key > 255:
            return
        self.fman.add_input( Floating(self.settings, "v>").error().put_text(f"Tecla char:{chr(key)}, code:{key}, não reconhecida") )


    def main(self, scr: curses.window):
        InputManager.fix_esc_delay()
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global

        while True:
            self.tree.update_tree(admin_mode=Flags.admin.is_true() or self.gui.search.search_mode)
            self.fman.draw_warnings()
            cman = self.make_callback()
            self.gui.show_items()

            if self.fman.has_floating():
                value: int = self.fman.get_input()
            else:
                value = scr.getch()
                value = InputManager.fix_cedilha(scr, value)

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
            if self.first_loop:
                self.first_loop = False

    def check_lang_in_text_mode(self):
        lang = self.rep.get_lang()
        if lang == "":
            options = available_languages
            print("\nLinguagem padrão ainda não foi definida.\n")
            while True:
                print("Escolha entre as opções a seguir ", end="")
                print("[" + ", ".join(options) + "]", ":", end=" ")
                lang = input()
                if lang in options:
                    break
            self.rep.set_lang(lang)


    def play(self):
        self.check_lang_in_text_mode()

        while True:
            output = curses.wrapper(self.main)
            if output is None:
                return
            else:
                output()
