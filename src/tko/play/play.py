from .keys import GuiKeys
from ..game.game import Game
from .opener import Opener
from typing import Any, Dict, Callable, Tuple
from ..settings.settings import Settings
from ..settings.app_settings import AppSettings
from ..settings.rep_settings import languages_avaliable, RepData
from ..util.sentence import Sentence
from .fmt import Fmt
from .search import Search
from .input_manager import InputManager


from .floating import Floating
from .floating_manager import FloatingManager
from .flags import Flag, Flags, FlagsMan
from .tasktree import TaskTree
from .gui import Gui
from .play_actions import PlayActions
from .functors import FlagFunctor, GradeFunctor

import os
import curses

class Play:
    def __init__(self, settings: Settings, game: Game, rep: RepData):
        self.settings = settings
        self.app = settings.app
        self.rep = rep
        self.game: Game = game

        self.exit = False

        if self.rep.get_lang() == "":
            self.rep.set_lang(self.app._lang_default)
        self.flagsman = FlagsMan(self.rep.get_flags())
        self.fman = FloatingManager()
        self.tree = TaskTree(self.settings, game, rep)
        self.gui = Gui(tree=self.tree, flagsman=self.flagsman, fman=self.fman)

        if len(self.rep.get_tasks()) == 0:
            self.gui.show_help()

        self.first_loop = True
        self.graph_ext = ""

        self.actions = PlayActions(self.gui)



    def save_to_json(self):
        self.tree.save_on_rep()
        self.rep.set_flags(self.flagsman.get_data())
        self.settings.save_settings()
        self.rep.save_data_to_json()

    def send_quit_msg(self):
        def set_exit():
            self.exit = True

        self.fman.add_input(
            Floating().put_text("\nAté a próxima\n").set_exit_fn(set_exit).warning()
        ),

    def toggle_config(self):
        if Flags.config.is_true():
            Flags.config.toggle()
            self.gui.config.disable()
        else:
            Flags.config.toggle()
            self.gui.config.enable()
            if Flags.skills.is_true():
                Flags.skills.toggle()

    def toggle_skills(self):
        if Flags.skills.is_true():
            Flags.skills.toggle()
        else:
            Flags.skills.toggle()
            if Flags.config.is_true():
                Flags.config.toggle()
            
    def process_tab(self):
        if Flags.config.is_true():
            self.gui.config.enable()

    def make_callback(self) -> InputManager:
        cman = InputManager()

        cman.add_int(curses.KEY_RESIZE, self.gui.disable_on_resize)
        cman.add_str(GuiKeys.key_quit, self.send_quit_msg)
        cman.add_int(InputManager.esc, self.send_quit_msg)
        cman.add_int(curses.KEY_BACKSPACE, self.send_quit_msg)

        if Flags.config.is_true() and self.gui.config.enabled:
            cman.add_str(GuiKeys.up, self.gui.config.move_up)
            cman.add_int(curses.KEY_UP, self.gui.config.move_up)
            cman.add_str(GuiKeys.down, self.gui.config.move_down)
            cman.add_int(curses.KEY_DOWN, self.gui.config.move_down)
            cman.add_str(GuiKeys.activate, self.gui.config.activate_selected)
            cman.add_int(InputManager.tab, self.gui.config.disable)
    
        else:
            cman.add_str(GuiKeys.up, self.tree.move_up)
            cman.add_int(curses.KEY_UP, self.tree.move_up)
            cman.add_str(GuiKeys.down, self.tree.move_down)
            cman.add_int(curses.KEY_DOWN, self.tree.move_down)
            cman.add_str(GuiKeys.left, self.tree.arrow_left)
            cman.add_int(curses.KEY_LEFT, self.tree.arrow_left)
            cman.add_str(GuiKeys.right, self.tree.arrow_right)
            cman.add_int(curses.KEY_RIGHT, self.tree.arrow_right)
            cman.add_str(GuiKeys.activate, self.actions.select_task)
            cman.add_int(InputManager.tab, self.process_tab)
            cman.add_str(GuiKeys.expand, self.tree.process_expand)
            cman.add_str(GuiKeys.expand2, self.tree.process_expand)
            cman.add_str(GuiKeys.collapse, self.tree.process_collapse)
            cman.add_str(GuiKeys.collapse2, self.tree.process_collapse)
            cman.add_str(GuiKeys.github_open, self.actions.open_link)
            cman.add_str(GuiKeys.down_task, self.actions.down_task)
            cman.add_str(GuiKeys.inc_grade, self.tree.inc_grade)
            cman.add_str(GuiKeys.inc_grade2, self.tree.inc_grade)
            cman.add_str(GuiKeys.dec_grade, self.tree.dec_grade)
            cman.add_str(GuiKeys.dec_grade2, self.tree.dec_grade)
            cman.add_str(GuiKeys.edit, lambda: self.actions.open_code())
            for value in range(1, 10):
                cman.add_str(str(value), GradeFunctor(int(value), self.tree.set_grade))
            cman.add_str("'", GradeFunctor(0, self.tree.set_grade))
            cman.add_str("0", GradeFunctor(10, self.tree.set_grade))
        
        cman.add_str(GuiKeys.key_help, self.gui.show_help)
        
        for flag in self.flagsman.others:
            cman.add_str(flag.get_keycode(), FlagFunctor(flag))

        config_elements = self.gui.config.get_elements()
        for element in config_elements:
            key = element.flag.get_keycode()
            fn = element.fn
            cman.add_str(key, fn)

        cman.add_str(Flags.config.get_keycode(), self.toggle_config)
        cman.add_str(Flags.skills.get_keycode(), self.toggle_skills)
        cman.add_str(GuiKeys.hud, self.app.toggle_hud)
        cman.add_str("/", self.gui.search.toggle_search)

        return cman
        
    def send_char_not_found(self, key):
        exclude_str = [ord(v) for v in [" ", "a", "d", "\n"]]
        exclude_int = [ -1, InputManager.esc, InputManager.left, InputManager.right ]
        if key in exclude_int + exclude_str:
            return
        self.fman.add_input(
            Floating("v")
                .error()
                .put_text(f"Tecla char {chr(key)} code {key} não reconhecida")
        )

    def main(self, scr):
        InputManager.fix_esc_delay()
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global

        while True:
            self.tree.update_tree(admin_mode=Flags.admin.is_true() or self.gui.search.search_mode)
            self.fman.draw_warnings()
            if self.gui.config.gen_graph:
                self.actions.generate_graph()
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
            options = languages_avaliable
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
