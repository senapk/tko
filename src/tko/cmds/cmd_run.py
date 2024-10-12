from typing import List, Optional
import os
import shutil
import subprocess

from tko.run.diff_builder_down import DownDiff
from tko.run.wdir import Wdir
from tko.util.consts import DiffCount, ExecutionResult
from tko.util.param import Param
from tko.run.diff_builder_side import SideDiff
from tko.util.text import Text, Token

from tko.util.consts import Success
from tko.util.raw_terminal import RawTerminal
from tko.util.symbols import symbols

from tko.util.freerun import Free
from tko.play.tester import Tester
from tko.run.unit_runner import UnitRunner
from tko.game.task import Task
from tko.play.opener import Opener
from tko.settings.settings import Settings
from tko.util.consts import DiffMode
from tko.util.logger import Logger, LogAction, LoggerFS
from tko.util.code_filter import CodeFilter
from tko.settings.repository import Repository

class TKOFilterMode:
    @staticmethod
    def deep_copy_and_change_dir():
        # path to ~/.tko_filter
        filter_path = os.path.join(os.path.expanduser("~"), ".tko_filter")

        CodeFilter.cf_recursive(".", filter_path, force=True)
        # verify if filter command is available
        # if shutil.which("filter_code") is None:
        #     print("ERROR: comando de filtragem não encontrado")
        #     print("Instale o feno com 'pip install feno'")
        #     exit(1)

        # subprocess.run(["filter_code", "-rf", ".", "-o", filter_path])

        os.chdir(filter_path)

class Run:

    def __init__(self, settings: Settings, target_list: List[str], exec_cmd: Optional[str], param: Optional[Param.Basic]):
        self.settings = settings
        self.target_list: List[str] = target_list
        self.exec_cmd: Optional[str] = exec_cmd
        if param is None:
            self.param = Param.Basic()
        else:
            self.param = param
        self.wdir: Wdir = Wdir()
        self.wdir_builded = False
        self.__curses_mode: bool = False
        self.__lang = ""
        self.__task: Optional[Task] = None
        self.__opener: Optional[Opener] = None
        self.__autorun: bool = True

    def set_curses(self, value:bool=True, success: Success=Success.RANDOM):
        self.__curses_mode = value
        return self
   
    def set_lang(self, lang:str):
        self.__lang = lang
        return self
    
    def set_opener(self, opener: Opener):
        self.__opener = opener
        return self

    def set_autorun(self, value:bool):
        self.__autorun = value

    def set_task(self, task: Task):
        self.__task = task
        return self
    
    def get_task(self) -> Task:
        if self.__task is None:
            raise Warning("Task não definida")
        return self.__task

    def execute(self):
        if not self.wdir_builded:
            self.build_wdir()

        if self.__missing_target():
            return
        if self.__list_mode():
            return
        
        if self.wdir.has_solver():
            if self.wdir.get_solver().path_list:
                Logger.instance = Logger(LoggerFS(self.settings))
                logger = Logger.instance
                solver_path = self.wdir.get_solver().path_list[0]
                dirname = os.path.dirname(os.path.abspath(solver_path))
                task_key = os.path.basename(dirname)
                upper_dir = os.path.dirname(dirname)
                log_file = os.path.join(upper_dir, Repository.LOG_FILE)
                if os.path.exists(log_file):
                    logger.set_log_file(log_file)
                if self.__task is None:
                    task = Task()
                    task.key = task_key
                    self.__task = task

        if self.__free_run():
            return
        self.__show_diff()
        return
    
    def __remove_duplicates(self):
        # remove duplicates in target list keeping the order
        self.target_list = list(dict.fromkeys(self.target_list))

    def __change_targets_to_filter_mode(self):
        if self.param.filter:
            old_dir = os.getcwd()

            print(Text(" Entrando no modo de filtragem ").center(RawTerminal.get_terminal_size(), "═"))
            TKOFilterMode.deep_copy_and_change_dir()  
            # search for target outside . dir and redirect target
            new_target_list = []
            for target in self.target_list:
                if ".." in target:
                    new_target_list.append(os.path.normpath(os.path.join(old_dir, target)))
                elif os.path.exists(target):
                    new_target_list.append(target)
            self.target_list = new_target_list

    def __print_top_line(self):
        if self.wdir is None:
            return

        print(Text().add(symbols.opening).add(self.wdir.resume()), end="")
        print(" [", end="")
        first = True
        for unit in self.wdir.get_unit_list():
            if first:
                first = False
            else:
                print(" ", end="")
            solver = self.wdir.get_solver()
            if solver is None:
                raise Warning("Solver vazio")
            unit.result = UnitRunner.run_unit(solver, unit)
            print(Text() + ExecutionResult.get_symbol(unit.result), end="")
        print("]")

    def __print_diff(self):
        if self.wdir is None or not self.wdir.has_solver():
            return
        
        if self.param.diff_count == DiffCount.QUIET:
            return
        
        if self.wdir.get_solver().compile_error:
            print(self.wdir.get_solver().error_msg)
            return
        
        results = [unit.result for unit in self.wdir.get_unit_list()]
        if ExecutionResult.EXECUTION_ERROR not in results and ExecutionResult.WRONG_OUTPUT not in results:
            return
        
        if not self.param.compact:
            for elem in self.wdir.unit_list_resume():
                print(elem)

        
        if self.param.diff_count == DiffCount.FIRST:
            # printing only the first wrong case
            wrong = [unit for unit in self.wdir.get_unit_list() if unit.result != ExecutionResult.SUCCESS][0]
            if self.param.diff_mode == DiffMode.DOWN:
                ud_diff_builder = DownDiff(RawTerminal.get_terminal_size(), wrong).to_insert_header()
                for line in ud_diff_builder.build_diff():
                    print(line)
            else:
                ss_diff_builder = SideDiff(RawTerminal.get_terminal_size(), wrong).to_insert_header(True)
                for line in ss_diff_builder.build_diff():
                    print(line)
            return

        if self.param.diff_count == DiffCount.ALL:
            for unit in self.wdir.get_unit_list():
                if unit.result != ExecutionResult.SUCCESS:
                    if self.param.diff_mode:
                        ud_diff_builder = DownDiff(RawTerminal.get_terminal_size(), unit).to_insert_header()
                        for line in ud_diff_builder.build_diff():
                            print(line)
                    else:
                        ss_diff_builder = SideDiff(RawTerminal.get_terminal_size(), unit).to_insert_header(True)
                        for line in ss_diff_builder.build_diff():
                            print(line)

    def build_wdir(self):
        self.wdir_builded = True
        self.__remove_duplicates()
        self.__change_targets_to_filter_mode()
        try:
            self.wdir = Wdir().set_curses(self.__curses_mode).set_lang(self.__lang).set_target_list(self.target_list).set_cmd(self.exec_cmd).build().filter(self.param)
        except FileNotFoundError as e:
            if self.wdir.has_solver():
                self.wdir.get_solver().error_msg += str(e)
                self.wdir.get_solver().compile_error = True
        return self.wdir

    def __missing_target(self) -> bool:
        if self.wdir is None:
            return False
        if not self.wdir.has_solver() and not self.wdir.has_tests():
            print(Text().addf("", "fail: ") + "Nenhum arquivo de código ou de teste encontrado.")
            return True
        return False
    
    def __list_mode(self) -> bool:
        if self.wdir is None:
            return False

        # list mode
        if not self.wdir.has_solver() and self.wdir.has_tests():
            print(Text("Nenhum arquivo de código encontrado. Listando casos de teste.").center(RawTerminal.get_terminal_size(), Token("╌")), flush=True)
            print(self.wdir.resume())
            for line in self.wdir.unit_list_resume():
                print(line)
            return True
        return False

    def __free_run(self) -> bool:
        if self.wdir is None:
            return False
        if self.wdir.has_solver() and (not self.wdir.has_tests()) and not self.__curses_mode:
            if self.__task is not None:
                Logger.get_instance().record_event(LogAction.FREE, self.get_task().key)
            Free.free_run(self.wdir.get_solver(), show_compilling=False, to_clear=False, wait_input=False)
            return True
        return False

    def __create_opener_for_wdir(self) -> Opener:
        opener = Opener(self.settings)
        folders = []
        targets = ["."]
        if self.target_list:
            targets = self.target_list
        for f in targets:
            if os.path.isdir(f) and f not in folders:
                folders.append(f)
            else:
                folder = os.path.dirname(os.path.abspath(f))
                if folder not in folders:
                    folders.append(folder)
        opener.set_target(folders)
        solver_zero = self.wdir.get_solver().path_list[0]
        lang = solver_zero.split(".")[-1]
        opener.set_language(lang)
        return opener

    def __show_diff(self):
        if self.wdir is None:
            return
        
        if self.__curses_mode:
            cdiff = Tester(self.settings, self.wdir)
            if self.__task is not None:
                cdiff.set_task(self.__task)
            if self.__opener is not None:
                cdiff.set_opener(self.__opener)
            else:
                cdiff.set_opener(self.__create_opener_for_wdir())
            cdiff.set_autorun(self.__autorun)
            cdiff.run()
        else:
            print(Text(" Testando o código com os casos de teste ").center(RawTerminal.get_terminal_size(), "═"))
            self.__print_top_line()
            self.__print_diff()
            correct = [unit for unit in self.wdir.get_unit_list() if unit.result == ExecutionResult.SUCCESS]
            percent = (len(correct) * 100) // len(self.wdir.get_unit_list())
            if self.__task is not None:
                Logger.get_instance().record_event(LogAction.TEST, self.get_task().key, str(percent) + "%")
