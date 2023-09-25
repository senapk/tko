from typing import List
import subprocess

from .wdir import Wdir
from .basic import DiffMode, ExecutionResult, CompilerError, Param, Unit
from .diff import Diff
from .format import Colored, Color, Report, symbols
from .writer import Writer
from .solver import Solver
from .runner import Runner


class Execution:

    def __init__(self):
        pass

    # run a unit using a solver and return if the result is correct
    @staticmethod
    def run_unit(solver: Solver, unit: Unit) -> ExecutionResult:
        cmd = solver.executable.split(" ")
        return_code, stdout, stderr = Runner.subprocess_run(cmd, unit.input)
        unit.user = stdout + stderr
        if return_code != 0:
            return ExecutionResult.EXECUTION_ERROR
        if unit.user == unit.output:
            return ExecutionResult.SUCCESS
        return ExecutionResult.WRONG_OUTPUT


class Actions:

    def __init__(self):
        pass

    @staticmethod
    def exec(target_list: List[str]):
        try:
            wdir = Wdir().set_target_list(target_list).build()
        except CompilerError as e:
            print(e)
            return 0

    @staticmethod
    def list(target_list: List[str], param: Param.Basic):
        wdir = Wdir().set_target_list(target_list).build().filter(param)


    @staticmethod
    def run(target_list: List[str], param: Param.Basic) -> int:
        try:
            wdir = Wdir().set_target_list(target_list).build().filter(param)
        except CompilerError as e:
            print(e)
            return 0
        except FileNotFoundError as e:
            print(e)
            return 0     

        if wdir.solver is None and len(wdir.unit_list) == 0:
            print(Colored.paint("fail: ", Color.RED) + "No solver or tests found.")
            return 0

        if wdir.solver is None and len(wdir.unit_list) > 0:
            print(wdir.resume())
            print(Report.centralize(" No solvers found. Listing Test Cases ", "╌"))
            print(wdir.unit_list_resume())
            return

        if wdir.solver is not None and len(wdir.unit_list) == 0:
            print(wdir.resume())
            print(Report.centralize(" No test cases found. Running: " + wdir.solver.executable + " ", symbols.hbar), flush=True)
            # force print to terminal

            subprocess.run(wdir.solver.executable, shell=True)
            return
        
        print(Report.centralize(" Running solver against test cases ", "═"))

        ## print top line
        print(wdir.resume(), end="")
        print("[ ", end="")
        for unit in wdir.unit_list:
            unit.result = Execution.run_unit(wdir.solver, unit)
            print(ExecutionResult.get_symbol(unit.result) + " ", end="")
        print("]")

        if param.diff_mode == DiffMode.QUIET:
            return
        
        results = [unit.result for unit in wdir.unit_list]
        if (ExecutionResult.EXECUTION_ERROR in results) or (ExecutionResult.WRONG_OUTPUT in results):
            # print cases lines
            print(wdir.unit_list_resume())
            
        if param.diff_mode == DiffMode.FIRST:
        # printing only the first wrong case
            wrong = [unit for unit in wdir.unit_list if unit.result != ExecutionResult.SUCCESS][0]
            if param.is_up_down:
                print(Diff.mount_up_down_diff(wrong))
            else:
                print(Diff.mount_side_by_side_diff(wrong))
            return

        if param.diff_mode == DiffMode.ALL:
            for unit in wdir.unit_list:
                if unit.result != ExecutionResult.SUCCESS:
                    if param.is_up_down:
                        print(Diff.mount_up_down_diff(unit))
                    else:
                        print(Diff.mount_side_by_side_diff(unit))
        return

    @staticmethod
    def build(target_out: str, source_list: List[str], param: Param.Manip, to_force: bool) -> bool:
        try:
            wdir = Wdir().set_sources(source_list).build()
            wdir.manipulate(param)
            Writer.save_target(target_out, wdir.unit_list, to_force)
        except FileNotFoundError as e:
            print(str(e))
            return False
        return True
