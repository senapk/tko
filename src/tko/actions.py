from typing import List
import subprocess

from .wdir import Wdir
from .basic import DiffMode, ExecutionResult, CompilerError, Param, Unit
from .diff import Diff
from .format import Symbol, Colored, Color, Report
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
            unit.user += Symbol.execution
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
        
        if wdir.solver is None:
            print("\n" + Colored.paint("fail:", Color.RED) + " no solver found\n")
            return        
        
        print(Report.centralize(" Exec " + wdir.solver.executable + " ", Symbol.hbar))
        subprocess.run(wdir.solver.executable, shell=True)

    @staticmethod
    def list(target_list: List[str], param: Param.Basic):
        wdir = Wdir().set_target_list(target_list).build().filter(param)
        print(wdir.resume())
        print(wdir.unit_list_resume())

    @staticmethod
    def run(target_list: List[str], param: Param.Basic) -> int:
        try:
            wdir = Wdir().set_target_list(target_list).build().filter(param)
        except CompilerError as e:
            print(e)
            return 0
        
        print(wdir.resume(), end="")

        if wdir.solver is None:
            print("\n" + Colored.paint("fail:", Color.RED) + " no solver found\n")
            return 0
        
        print("[ ", end="")
        for unit in wdir.unit_list:
            unit.result = Execution.run_unit(wdir.solver, unit)
            print(unit.result.value + " ", end="")
        print("]\n")

        if param.diff_mode != DiffMode.QUIET:        
            results = [unit.result for unit in wdir.unit_list]
            if (ExecutionResult.EXECUTION_ERROR in results) or (ExecutionResult.WRONG_OUTPUT in results):
                print(wdir.unit_list_resume())

                wrong = [unit for unit in wdir.unit_list if unit.result != ExecutionResult.SUCCESS][0]
                if param.is_up_down:
                    print(Diff.mount_up_down_diff(wrong))
                else:
                    print(Diff.mount_side_by_side_diff(wrong))
        return wdir.calc_grade()

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
