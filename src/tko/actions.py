from typing import List, Optional
import os
import shutil
import subprocess

from .run.wdir import Wdir
from .run.basic import DiffMode, ExecutionResult, CompilerError, Param, Unit
from .run.diff import Diff

from .run.report import Report
from .util.term_color import colour
from .util.symbols import symbols

from .run.writer import Writer
from .run.solver import Solver
from .util.runner import Runner


class Execution:

    def __init__(self):
        pass

    # run a unit using a solver and return if the result is correct
    @staticmethod
    def run_unit(solver: Solver, unit: Unit) -> ExecutionResult:
        cmd = solver.executable
        return_code, stdout, stderr = Runner.subprocess_run(cmd, unit.input)
        unit.user = stdout + stderr
        if return_code != 0:
            return ExecutionResult.EXECUTION_ERROR
        if unit.user == unit.output:
            return ExecutionResult.SUCCESS
        return ExecutionResult.WRONG_OUTPUT


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
        self.target_list = target_list
        self.exec_cmd = exec_cmd
        self.param = param
        self.wdir = None

    def execute(self):
        self.remove_duplicates()
        self.change_targets_to_filter_mode()
        if not self.build_wdir():
            return
        if self.missing_target():
            return
        if self.list_mode():
            return
        if self.free_run():
            return
        self.diff_mode()
        return

    def remove_duplicates(self):
        # remove duplicates in target list keeping the order
        self.target_list = list(dict.fromkeys(self.target_list))

    def change_targets_to_filter_mode(self):
        if self.param.filter:
            old_dir = os.getcwd()

            print(Report.centralize(" Entering in filter mode ", "═"))
            FilterMode.deep_copy_and_change_dir()  
            # search for target outside . dir and redirect target
            new_target_list = []
            for target in self.target_list:
                if ".." in target:
                    new_target_list.append(os.path.normpath(os.path.join(old_dir, target)))
                elif os.path.exists(target):
                    new_target_list.append(target)
            self.target_list = new_target_list

    def print_top_line(self):
        print(self.wdir.resume(), end="")
        print(" [", end="", flush=True)
        first = True
        for unit in self.wdir.unit_list:
            if first:
                first = False
            else:
                print(" ", end="", flush=True)
            unit.result = Execution.run_unit(self.wdir.solver, unit)
            print(ExecutionResult.get_symbol(unit.result), end="", flush=True)
        print("]")

    def print_diff(self):
        if self.param.diff_mode == DiffMode.QUIET:
            return
        
        results = [unit.result for unit in self.wdir.unit_list]
        if ExecutionResult.EXECUTION_ERROR not in results and ExecutionResult.WRONG_OUTPUT not in results:
            return
        
        if not self.param.compact:
            print(self.wdir.unit_list_resume())
        
        if self.param.diff_mode == DiffMode.FIRST:
            # printing only the first wrong case
            wrong = [unit for unit in self.wdir.unit_list if unit.result != ExecutionResult.SUCCESS][0]
            if self.param.is_up_down:
                print(Diff.mount_up_down_diff(wrong))
            else:
                print(Diff.mount_side_by_side_diff(wrong))
            return

        if self.param.diff_mode == DiffMode.ALL:
            for unit in self.wdir.unit_list:
                if unit.result != ExecutionResult.SUCCESS:
                    if self.param.is_up_down:
                        print(Diff.mount_up_down_diff(unit))
                    else:
                        print(Diff.mount_side_by_side_diff(unit))

    def build_wdir(self) -> bool:
        try:
            self.wdir = Wdir().set_target_list(self.target_list).set_cmd(self.exec_cmd).build().filter(self.param)
        except CompilerError as e:
            print(e)
            return False
        except FileNotFoundError as e:
            print(e)
            return False
        return True

    def missing_target(self) -> bool:
        # no solver and no test cases
        if self.wdir.solver is None and len(self.wdir.unit_list) == 0:
            print(colour("red", "fail: ") + "No solver or tests found.")
            return True
        return False
    
    def list_mode(self) -> bool:
        # list mode
        if self.wdir.solver is None and len(self.wdir.unit_list) > 0:
            print(Report.centralize(" No solvers found. Listing Test Cases ", "╌"), flush=True)
            print(self.wdir.resume())
            print(self.wdir.unit_list_resume())
            return True
        return False

    def free_run(self) -> bool:
        # free run mode
        if self.wdir.solver is not None and len(self.wdir.unit_list) == 0:
            t = Report.centralize(" No test cases found. Running: " + self.wdir.solver.executable + " ", symbols.hbar)
            print(t, flush=True)
            # force print to terminal
            Runner.free_run(self.wdir.solver.executable)
            return True
        return False

    def diff_mode(self):
        print(Report.centralize(" Running solver against test cases ", "═"))
        self.print_top_line()
        self.print_diff()


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
