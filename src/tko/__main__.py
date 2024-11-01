from __future__ import annotations

import argparse
import sys

from tko.util.text import Text
from tko.util.decoder import Decoder

from tko.cmds.cmd_rep import CmdRep
from tko.cmds.cmd_play import CmdPlay
from tko.cmds.cmd_down import CmdDown
from tko.cmds.cmd_run import Run
from tko.cmds.cmd_build import CmdBuild
from tko.cmds.cmd_config import CmdConfig, ConfigParams
from tko.util.logger import LogAction, Logger, LoggerFS
from tko.util.text import AnsiColor

from tko.util.param import Param
from tko.util.pattern import PatternLoader
from tko.util.consts import DiffCount, DiffMode
from tko.settings.settings import Settings

from tko.settings.repository import Repository

from tko.util.guide import tko_guide
from tko.util.guide import bash_guide

from tko.util.raw_terminal import RawTerminal
from tko.util.symbols import symbols
from tko.settings.check_version import CheckVersion

import os

from tko.__init__ import __version__


class Main:
    @staticmethod
    def test(args):
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        if args.quiet:
            param.set_diff_count(DiffCount.QUIET)
        elif args.all:
            param.set_diff_count(DiffCount.ALL)
        else:
            param.set_diff_count(DiffCount.FIRST)

        if args.filter:
            param.set_filter(True)
        if args.compact:
            param.set_compact(True)

        settings = Settings()
        if not args.side and not args.down:
            param.set_diff_mode(settings.app.get_diff_mode())
        elif args.side:
            param.set_diff_mode(DiffMode.SIDE)
        elif args.down:
            param.set_diff_mode(DiffMode.DOWN)
        cmd_run = Run(settings, args.target_list, param)
        cmd_run.execute()

    @staticmethod
    def run(args):
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        settings = Settings()
        param.set_diff_mode(settings.app.get_diff_mode())
        if args.filter:
            param.set_filter(True)
        cmd_run = Run(settings, args.target_list, param)
        cmd_run.set_curses()
        cmd_run.execute()

    @staticmethod
    def build(args):
        PatternLoader.pattern = args.pattern
        manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
        build = CmdBuild(args.target, args.target_list, manip)
        build.execute()

    @staticmethod
    def play(args):
        settings = Settings()
        if settings.has_alias_folder(args.alias):
            folder = settings.get_alias_folder(args.alias)
            if not os.path.exists(folder):
                settings.del_alias_folder(args.alias)
                settings.save_settings()
                print(Text("{r}: o diretório {g} não existe mais.", "Falha", folder))
                return
            rep = Repository(folder)
            if not rep.has_local_config_file():
                print(Text("{r}: o diretório {g} não é um repositório válido.", "Falha", folder))
                return
            CmdPlay(settings).load_folder(folder).execute()
        else:
            print(Text("{r}: não existe nenhum repositório local cadastrado para o atalho {y}.", "Falha", args.alias))
            print(Text("{g}: utilize o comando {y} para iniciar um repositório local.", "Atenção", "tko start [fup|poo|ed]"))
            print(Text("{g}: {y}", "Exemplo", "tko start fup"))
        CheckVersion().version_check()

    @staticmethod
    def save(args):
        if not os.path.exists(args.folder) or not os.path.isdir(args.folder):
            print(Text("{r}: o diretório {g} não existe.", "Falha", args.folder))
            return

        settings = Settings()
        rep = Repository(args.folder)
        if not rep.has_local_config_file():
            print(Text("{r}: o diretório {g} não é um repositório válido.", "Falha", args.folder))
            return
        
        settings.set_alias_folder(args.alias, args.folder)
        print(Text("{g}: repositório {g} salvo com o atalho {g}.", "Sucesso", args.folder, args.alias))

    # @staticmethod
    # def play(args):
    #     print(Text("{g}: utilize o comando '{y}' para abrir um repositório local cadastrado.", "Atenção", "tko load " + args.alias))

    @staticmethod
    def open(args):
        settings = Settings()
        CmdPlay(settings).load_folder(args.folder).execute()

    @staticmethod
    def init(args):
        remote: str | None = args.remote
        url: str | None = args.url
        file: str | None = args.file
        folder: str | None = args.folder
        save: str | None = args.save
        Main.__init(remote=remote, url=url, file=file, folder=folder, save=save)

    @staticmethod
    def __init(remote: str | None, url: str | None, file: str | None, folder: str | None, save: str | None):
        if folder is None:
            folder = os.getcwd()
            print("Deseja criar um repositório em " + folder + "? (s/n): ", end="")
            op = input()
            if op == "n":
                return
        rep = Repository(os.path.abspath(folder))
        if remote is None and url is None and file is None:
            index = rep.get_default_readme_path()
            print("Nenhuma fonte foi informada, utilizando o arquivo {} como fonte".format(index))
            if not os.path.exists(index):
                content = "# Repositório\n\n## Grupo\n\n### Missão\n\n- [ ] [#google Abra o google](https://www.google.com)\n"
                Decoder.save(index, content)

        else:
            settings = Settings()
            source: str = ""
            if remote is not None:
                if settings.has_alias_remote(remote):
                    source = settings.get_alias_remote(remote)
                else:
                    raise Warning("fail: alias remoto não encontrado.")
            elif url is not None:
                source = url
            elif file is not None:
                source = file
            rep.set_remote_source(source)
        rep.save_data_to_config_file()
        if save is not None:
            settings = Settings()
            settings.set_alias_folder(save, folder)
            settings.save_settings()

    @staticmethod
    def start(args):
        remote: str = args.remote
        Main.__init(remote=remote, url=None, file=None, folder=remote, save=remote)
        print(Text("Repositório {g} criado com sucesso na pasta {g}", remote, os.path.abspath(remote)))
        print(Text("O atalho {g} foi vinculado a essa pasta, para acessá-lo", remote))
        print(Text("basta utilizar o comando {g}", "tko play " + remote))

    # @staticmethod
    # def down(args):
    #     settings = Settings()
    #     settings.check_rootdir()
    #     cmd_down = CmdDown(rep=args.course, task_key=args.activity, settings=settings)
    #     cmd_down.set_language(args.language).set_fnprint(print)
    #     cmd_down.execute()

    @staticmethod
    def config(args):
        settings = Settings()
        param = ConfigParams()
        param.side = args.side
        param.down = args.down
        param.images = args.images
        param.editor = args.editor
        param.borders = args.borders
        param.timeout = args.timeout

        CmdConfig.execute(settings, param)

    @staticmethod
    def list(_args):
        settings = Settings()
        print(str(settings))


class Parser:
    def __init__(self):
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(prog='tko', description=f'tko version {__version__}')
        self.subparsers = self.parser.add_subparsers(title='subcommands', help='help for subcommand.')

        self.parent_manip = self.create_parent_manip()
        self.parent_basic = self.create_parent_basic()

        self.add_parser_global()
        self.create_parent_basic()
        self.create_parent_manip()
        self.add_parser_run()
        self.add_parser_exec()
        self.add_parser_build()
        # self.add_parser_down()
        self.add_parser_config()
        self.add_parser_rep_tools()
        self.add_parser_rep_actions()
        # self.add_parser_open()
        # self.add_parser_save()
        # self.add_parser_init()


    def add_parser_global(self):
        self.parser.add_argument('-c', metavar='CONFIG_FILE', type=str, help='config json file.')
        self.parser.add_argument('-w', metavar='WIDTH', type=int, help="terminal width.")
        self.parser.add_argument('-v', action='store_true', help='show version.')
        self.parser.add_argument('-m', action='store_true', help='monochromatic.')

    def create_parent_basic(self):
        parent_basic = argparse.ArgumentParser(add_help=False)
        parent_basic.add_argument('--index', '-i', metavar="I", type=int, help='run a specific index.')
        parent_basic.add_argument('--pattern', '-p', metavar="P", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')
        return parent_basic

    def create_parent_manip(self):
        parent_manip = argparse.ArgumentParser(add_help=False)
        parent_manip.add_argument('--width', '-w', type=int, help="term width.")
        parent_manip.add_argument('--unlabel', '-u', action='store_true', help='remove all labels.')
        parent_manip.add_argument('--number', '-n', action='store_true', help='number labels.')
        parent_manip.add_argument('--sort', '-s', action='store_true', help="sort test cases by input size.")
        parent_manip.add_argument('--pattern', '-p', metavar="@.in @.out", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')
        return parent_manip

    def add_parser_run(self):
        parser_r = self.subparsers.add_parser('run', parents=[self.parent_basic], help='Run with test cases using curses.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--filter', '-f', action='store_true', help='filter solver in temp dir before run')
        parser_r.set_defaults(func=Main.run)

    def add_parser_exec(self):
        parser_r = self.subparsers.add_parser('test', parents=[self.parent_basic], help='Run with test cases using raw terminal.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--filter', '-f', action='store_true', help='filter solver in temp dir before run')
        parser_r.add_argument('--compact', '-c', action='store_true', help='Do not show case descriptions in failures')

        group_n = parser_r.add_mutually_exclusive_group()
        group_n.add_argument('--quiet', '-q', action='store_true', help='quiet mode, do not show any failure.')
        group_n.add_argument('--all', '-a', action='store_true', help='show all failures.')

        # add an exclusive group for diff mode
        group = parser_r.add_mutually_exclusive_group()
        group.add_argument('--down', '-d', action='store_true', help="diff mode up-to-down.")
        group.add_argument('--side', '-s', action='store_true', help="diff mode side-by-side.")
        parser_r.set_defaults(func=Main.test)

    def add_parser_build(self):
        parser_b = self.subparsers.add_parser('build', parents=[self.parent_manip], help='Build a test target.')
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='target to be build.')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        parser_b.set_defaults(func=Main.build)

    # def add_parser_down(self):
    #     parser_d = self.subparsers.add_parser('down', help='download problem from repository.')
    #     parser_d.add_argument('course', type=str, nargs='?', help=" [ fup | ed | poo ].")
    #     parser_d.add_argument('activity', type=str, nargs='?', help="activity @label.")
    #     parser_d.add_argument('--language', '-l', type=str, nargs='?', help="[ c | cpp | js | ts | py | java ]")
    #     parser_d.set_defaults(func=Main.down)

    def add_parser_config(self):
        parser_cfg = self.subparsers.add_parser('config', help='Settings tool.')
        subpar_repo = parser_cfg.add_subparsers(title='subcommands', help='help for subcommand.')

        cfg_reset = subpar_repo.add_parser('reset', help='reset all repositories, folders and values to factory default.')
        cfg_reset.set_defaults(func=CmdRep.reset)

        cfg_set = subpar_repo.add_parser('set', help='set default config values.')

        g_diff = cfg_set.add_mutually_exclusive_group()
        g_diff.add_argument('--side', action='store_true', help='set side_by_side diff mode.')
        g_diff.add_argument('--down', action='store_true', help='set up_to_down   diff mode.')

        # g_lang = parser_s.add_mutually_exclusive_group()
        # g_lang.add_argument("--lang", '-l', metavar='ext', type=str, help="set default language extension.")
        # g_lang.add_argument("--ask", action='store_true', help='ask language extension every time.')

        # parser_s.add_argument("--root", metavar="path", type=str, help='set root directory.')
        cfg_set.add_argument("--editor", metavar="cmd", type=str, help='set editor command.')
        cfg_set.add_argument("--borders", metavar="[0|1]", type=str, help='enable borders.')
        cfg_set.add_argument("--images", metavar="[0|1]", type=str, help='enable images.')
        cfg_set.add_argument("--timeout", metavar="sec", type=int, help='set timeout.')

        cfg_set.set_defaults(func=Main.config)

        cfg_list = subpar_repo.add_parser('list', help='list default config values.')
        cfg_list.set_defaults(func=Main.list)



    def add_parser_rep_tools(self):

        parser_repo = self.subparsers.add_parser('rep', help='Repository validation tools.')
        subpar_repo = parser_repo.add_subparsers(title='subcommands', help='help for subcommand.')

        # repo_reset = subpar_repo.add_parser('reset', help='reset all repositories and folders to factory default.')
        # repo_reset.set_defaults(func=CmdRep.reset)

        # repo_graph = subpar_repo.add_parser('graph', help='generate graph of the repository.')
        # repo_graph.add_argument('alias', metavar='alias', type=str, help='alias of the repository to be graphed.')
        # repo_graph.set_defaults(func=CmdRep.graph)

        repo_log = subpar_repo.add_parser("check", help="validates log of the repository.")
        repo_log.add_argument('folder', type=str, help='folder to be checked.')
        repo_log.set_defaults(func=CmdRep.check)

    # def add_parser_save(self):
    #     parser_p = self.subparsers.add_parser('save', help='Save a repository folder with a global alias.')
    #     parser_p.add_argument('folder', type=str, help='repository folder.')
    #     parser_p.add_argument('alias', type=str, help='repository alias.')
    #     parser_p.set_defaults(func=CmdRep.save)

    def add_parser_rep_actions(self):
        # parser_load = self.subparsers.add_parser('load', help='Load a saved repository.')
        # parser_load.add_argument('alias', type=str, help='repository alias.')
        # parser_load.set_defaults(func=Main.load)

        parser_play = self.subparsers.add_parser('play', help='Load and play a saved repository.')
        parser_play.add_argument('alias', type=str, help='repository alias.')
        parser_play.set_defaults(func=Main.play)

        parser_open = self.subparsers.add_parser('open', help='Open a folder with a repository.')
        parser_open.add_argument('folder', type=str, help='folder.')
        parser_open.set_defaults(func=Main.open)

        parser_save = self.subparsers.add_parser('save', help='Save a repository in a global alias.')
        parser_save.add_argument('alias', type=str, help='alias.')
        parser_save.add_argument('folder', type=str, help='folder.')
        parser_save.set_defaults(func=Main.save)

        parser_init = self.subparsers.add_parser('init', help='Initialize a repository in a folder.')

        source = parser_init.add_mutually_exclusive_group()
        source.add_argument('--remote', type=str, help='remote source [fup|ed|poo].')
        source.add_argument('--url', type=str, help='remote url.')
        source.add_argument('--file', type=str, help='remote or local file.')

        parser_init.add_argument('--folder', type=str, help='local directory.')
        parser_init.add_argument('--save', metavar="alias", type=str, help='save in global alias.')
        parser_init.set_defaults(func=Main.init)

        parser_start = self.subparsers.add_parser('start', help='Initialize a repository in a folder with a remote source and save in alias.')
        parser_start.add_argument('remote', type=str, help='remote source [fup|ed|poo].')
        parser_start.set_defaults(func=Main.start)


    # def add_parser_open(self):


    # def add_parser_init(self):
    #     parser_p = self.subparsers.add_parser('open', help='open a folder with a repository.')
    #     parser_p.add_argument('folder', metavar='folder', type=str, help='folder.')
    #     parser_p.set_defaults(func=CmdRep.init)



def exec(parser: argparse.ArgumentParser, args):
    settings = Settings()
    if args.w is not None:
        RawTerminal.set_terminal_size(args.w)
    if args.c:
        settings.set_settings_file(args.c)
    settings.load_settings()
    Logger.instance = Logger(LoggerFS(settings))

    if args.m:
        AnsiColor.enabled = False
    else:
        AnsiColor.enabled = True
        symbols.set_colors()

    if args.v:
        if args.v:
            print("tko version " + __version__)
    else:
        if "func" in args:
            args.func(args)
        else:
            parser.print_help()

def main():
    try:
        parser = Parser().parser
        args = parser.parse_args()
        exec(parser, args)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt")
        sys.exit(1)
    except Warning as w:
        print("")
        print(w)
        sys.exit(1)
    # except Exception as e:
    #     print(e)
    #     sys.exit(1)

# NÃO RETIRE ESSA TAG POR CAUSA DO MERGE DO REPLIT
if __name__ == '__main__': # MERGE_INSERT 
    main()
