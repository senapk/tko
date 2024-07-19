from typing import List, Optional
import os
import shutil
import subprocess

from .run.wdir import Wdir
from .run.basic import DiffMode, ExecutionResult, CompilerError, Param
from .run.diff import Diff
from .util.ftext import Sentence, Token

from .run.report import Report
from .util.term_color import term_print
from .util.symbols import symbols

from .run.writer import Writer
from .util.runner import Runner
from .cdiff import CDiff
from .execution import Execution



class FilterMode:

    @staticmethod
    def deep_copy_and_change_dir():
        # path to ~/.tko_filter
        filter_path = os.path.join(os.path.expanduser("~"), ".tko_filter")

        # verify if filter command is available
        if shutil.which("filter") is None:
            print("ERROR: filter command not found")
            print("Install feno with 'pip install feno'")
            exit(1)

        subprocess.run(["filter", "-rf", ".", "-o", filter_path])

        os.chdir(filter_path)


class Run:

    def __init__(self, target_list: List[str], exec_cmd: Optional[str], param: Param.Basic):
        self.target_list: List[str] = target_list
        self.exec_cmd: Optional[str] = exec_cmd
        self.param: Param.Basic = param
        self.wdir: Wdir = Wdir()
        self.curses: bool = False

    def set_curses(self, value:bool=True):
        self.curses = value
        return self

    def execute(self):
        self.__remove_duplicates()
        self.__change_targets_to_filter_mode()
        if not self.__build_wdir():
            return
        if self.__missing_target():
            return
        if self.__list_mode():
            return
        if self.__free_run():
            return
        self.__diff_mode()
        return

    def __remove_duplicates(self):
        # remove duplicates in target list keeping the order
        self.target_list = list(dict.fromkeys(self.target_list))

    def __change_targets_to_filter_mode(self):
        if self.param.filter:
            old_dir = os.getcwd()

            term_print(Report.centralize(" Entering in filter mode ", "═"))
            FilterMode.deep_copy_and_change_dir()  
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

        term_print(symbols.opening + self.wdir.resume(), end="")
        term_print(" [", end="")
        first = True
        for unit in self.wdir.unit_list:
            if first:
                first = False
            else:
                term_print(" ", end="")
            solver = self.wdir.solver
            if solver is None:
                raise ValueError("Solver empty")
            unit.result = Execution.run_unit(solver, unit)
            term_print(Sentence() + ExecutionResult.get_symbol(unit.result), end="")
        term_print("]")

    def __print_diff(self):
        if self.wdir is None or self.wdir.solver is None:
            return
        
        if self.param.diff_mode == DiffMode.QUIET:
            return
        
        if self.wdir.solver.compile_error:
            term_print(self.wdir.solver.error_msg)
            return
        
        results = [unit.result for unit in self.wdir.unit_list]
        if ExecutionResult.EXECUTION_ERROR not in results and ExecutionResult.WRONG_OUTPUT not in results:
            return
        
        if not self.param.compact:
            for elem in self.wdir.unit_list_resume():
                term_print(elem)
        
        if self.param.diff_mode == DiffMode.FIRST:
            # printing only the first wrong case
            wrong = [unit for unit in self.wdir.unit_list if unit.result != ExecutionResult.SUCCESS][0]
            if self.param.is_up_down:
                for line in Diff.mount_up_down_diff(wrong):
                    term_print(line)
            else:
                for line in Diff.mount_side_by_side_diff(wrong):
                    term_print(line)
            return

        if self.param.diff_mode == DiffMode.ALL:
            for unit in self.wdir.unit_list:
                if unit.result != ExecutionResult.SUCCESS:
                    if self.param.is_up_down:
                        for line in Diff.mount_up_down_diff(unit):
                            term_print(line)
                    else:
                        for line in Diff.mount_side_by_side_diff(unit):
                            term_print(line)

    def __build_wdir(self) -> bool:
        try:
            self.wdir = Wdir().set_curses(self.curses).set_target_list(self.target_list).set_cmd(self.exec_cmd).build().filter(self.param)
        except FileNotFoundError as e:
            if self.wdir.solver is not None:
                self.wdir.solver.error_msg += str(e)
                self.wdir.solver.compile_error = True
        return True

    def __missing_target(self) -> bool:
        if self.wdir is None:
            return False
        # no solver and no test cases
        if self.wdir.solver is None and len(self.wdir.unit_list) == 0:
            term_print(Sentence().addf("", "fail: ") + "No solver or tests found.")
            return True
        return False
    
    def __list_mode(self) -> bool:
        if self.wdir is None:
            return False

        # list mode
        if self.wdir.solver is None and len(self.wdir.unit_list) > 0:
            term_print(Report.centralize(" No solvers found. Listing Test Cases ", Token("╌")), flush=True)
            term_print(self.wdir.resume())
            for line in self.wdir.unit_list_resume():
                term_print(line)
            return True
        return False

    def __free_run(self) -> bool:
        if self.wdir is None:
            return False
        # free run mode
        if self.wdir.solver is not None and len(self.wdir.unit_list) == 0:
            t = Report.centralize(Sentence() + " No test cases found. Running: " + self.wdir.solver.executable + " ", symbols.hbar)
            term_print(t, flush=True)
            # force print to terminal
            Runner.free_run(self.wdir.solver.executable)
            return True
        return False

    def __diff_mode(self):
        if self.wdir is None:
            return
        
        if self.curses:
            cdiff = CDiff(self.wdir, self.param)
            cdiff.run()
            return
        term_print(Report.centralize(" Running solver against test cases ", "═"))
        self.__print_top_line()
        self.__print_diff()


class Build:

    def __init__(self, target_out: str, source_list: List[str], param: Param.Manip, to_force: bool):
        self.target_out = target_out
        self.source_list = source_list
        self.param = param
        self.to_force = to_force

    def execute(self):
        try:
            wdir = Wdir().set_sources(self.source_list).build()
            wdir.manipulate(self.param)
            Writer.save_target(self.target_out, wdir.unit_list, self.to_force)
        except FileNotFoundError as e:
            print(str(e))
            return False
        return True
