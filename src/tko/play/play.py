from ..game.game import Game
from .opener import Opener
from typing import List, Any, Dict, Callable, Tuple
from ..settings.settings import Settings
from ..settings.app_settings import AppSettings
from ..settings.rep_settings import languages_avaliable, RepData
from ..util.sentence import Sentence
from .fmt import Fmt
from .search import Search


from .floating import Floating
from .floating_manager import FloatingManager
from .flags import Flag, Flags, FlagsMan
from .tasktree import TaskTree
from .gui import Gui, Key
from .play_actions import PlayActions
from .functors import FlagFunctor, GradeFunctor

import os
import curses

class Play:
    def __init__(
        self,
        app: AppSettings,
        game: Game,
        rep_data: RepData,
        rep_alias: str
    ):
        self.app = app
        self.rep_alias = rep_alias
        self.rep = rep_data
        self.settings = Settings()
        self.exit = False

        if self.rep.get_lang() == "":
            self.rep.set_lang(self.app.get_lang_def())
        self.flagsman = FlagsMan(self.rep.get_flags())
        
        self.game: Game = game
        self.fman = FloatingManager()
        self.tree = TaskTree(app, game, rep_data, rep_alias)
        self.search = Search(tree=self.tree, fman=self.fman, game=self.game)
        self.gui = Gui(rep=self.rep, rep_alias=self.rep_alias, game=self.game, tree=self.tree, 
                       flagsman=self.flagsman, search=self.search, fman=self.fman)

        if len(self.rep.get_tasks()) == 0:
            self.gui.show_help()

        self.first_loop = True
        self.graph_ext = ""

        self.opener = Opener(tree=self.tree, fman=self.fman, geral=app, rep_data=rep_data, rep_alias=rep_alias)
        self.actions = PlayActions(fman=self.fman, rep=self.rep, rep_alias=self.rep_alias, tree=self.tree, game=self.game, opener=self.opener, gui=self.gui)

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
        else:
            Flags.config.toggle()

    def make_callback(self) -> Dict[int, Any]:
        calls: Dict[int, Callable[[],None]] = {}

        def add_int(_key: int, fn):
            if _key in calls.keys():
                raise ValueError(f"Chave duplicada {chr(_key)}")
            calls[_key] = fn

        def add_str(str_key: str, fn):
            if str_key != "":
                add_int(ord(str_key), fn)

        add_int(curses.KEY_RESIZE, self.gui.disable_on_resize)
        add_str(Key.quit, self.send_quit_msg)
        add_int(27, self.send_quit_msg)
        add_int(curses.KEY_BACKSPACE, self.send_quit_msg)


        add_str(Key.up, self.tree.move_up)
        add_int(curses.KEY_UP, self.tree.move_up)

        add_str(Key.down, self.tree.move_down)
        add_int(curses.KEY_DOWN, self.tree.move_down)

        add_str(Key.left, self.tree.arrow_left)
        add_int(curses.KEY_LEFT, self.tree.arrow_left)

        add_str(Key.right, self.tree.arrow_right)
        add_int(curses.KEY_RIGHT, self.tree.arrow_right)

        add_str(Key.ajuda, self.gui.show_help)
        add_str(Key.expand, self.tree.process_expand)
        add_str(Key.expand2, self.tree.process_expand)
        add_str(Key.collapse, self.tree.process_collapse)
        add_str(Key.collapse2, self.tree.process_collapse)
        add_str(Key.github_open, self.actions.open_link)
        add_str(Key.set_lang, lambda: self.actions.set_language(False))
        add_str(Key.set_root_dir, lambda: self.actions.set_rootdir(False))
        add_str(Key.down_task, self.actions.down_task)
        add_str(Key.select_task, self.actions.select_task)
        add_str("t", lambda: self.fman.add_input(Floating().put_text("\n Use o Enter para testar uma questão\n").warning()))
        add_str(Key.inc_grade, self.tree.inc_grade)
        add_str(Key.inc_grade2, self.tree.inc_grade)
        add_str(Key.dec_grade, self.tree.dec_grade)
        add_str(Key.dec_grade2, self.tree.dec_grade)
        add_str(Key.edit, lambda: self.opener.open_code(open_dir=True))
        add_str(Key.cores, self.app.toggle_color)
        add_str(Key.bordas, self.app.toggle_nerdfonts)
        add_str(Key.graph, self.actions.graph_toggle)

        for value in range(1, 10):
            add_str(str(value), GradeFunctor(int(value), self.tree.set_grade))
        add_str("'", GradeFunctor(0, self.tree.set_grade))
        add_str("0", GradeFunctor(10, self.tree.set_grade))

        for flag in self.flagsman.left:
            add_str(flag.get_char(), FlagFunctor(self.fman, flag))
        for flag in self.flagsman.others:
            add_str(flag.get_char(), FlagFunctor(self.fman, flag))

        add_str(Flags.config.get_char(), self.toggle_config)
        add_str(Flags.skills.get_char(), FlagFunctor(self.fman, Flags.skills))
        add_str("/", self.search.toggle_search)

        return calls
        
    def send_char_not_found(self, key):
        self.fman.add_input(
            Floating("v>")
                .error()
                .put_text("Tecla")
                .put_text(f"char {chr(key)}")
                .put_text(f"code {key}")
                .put_text("não reconhecida")
                .put_text("")
        )

    def main(self, scr):
        if hasattr(curses, "set_escdelay"):
            curses.set_escdelay(25)
        else:
            os.environ.setdefault('ESCDELAY', '25')
        # verify if curses has method set_escdelay
        curses.curs_set(0)  # Esconde o cursor
        Fmt.init_colors()  # Inicializa as cores
        Fmt.set_scr(scr)  # Define o scr como global

        while True:
            self.tree.update_tree(admin_mode=Flags.admin.is_true() or self.search.search_mode)
            self.fman.draw_warnings()
            if self.gui.gen_graph:
                self.actions.generate_graph()
            calls = self.make_callback()
            self.gui.show_items()

            if self.fman.has_floating():
                value: int = self.fman.get_input()
            else:
                value = scr.getch()
                if value == 195:
                    value = scr.getch()
                    if value == 167: #ç
                        value = ord("c")

            if self.exit:
                break

            if self.search.search_mode:
                self.search.process_search(value)
            elif value in calls.keys():
                callback = calls[value]()
                if callback is not None:
                    return callback
            elif value != -1 and value != 27 and value != 32:
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

    def play(self, graph_ext: str):
        self.graph_ext = graph_ext
        self.check_lang_in_text_mode()

        while True:
            output = curses.wrapper(self.main)
            if output is None:
                return
            else:
                output()
