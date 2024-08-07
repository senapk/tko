from .run.unit import Unit
from .run.basic import ExecutionResult

from .util.runner import Runner
from .run.solver import Solver

class Execution:

    def __init__(self):
        pass

    # run a unit using a solver and return if the result is correct
    @staticmethod
    def run_unit(solver: Solver, unit: Unit) -> ExecutionResult:
        if solver.compile_error:
            unit.user = solver.error_msg
            return ExecutionResult.COMPILATION_ERROR
        cmd = solver.get_executable()
        return_code, stdout, stderr = Runner.subprocess_run(cmd, unit.input)
        unit.user = stdout + stderr
        if return_code != 0:
            return ExecutionResult.EXECUTION_ERROR
        if unit.user == unit.output:
            return ExecutionResult.SUCCESS
        return ExecutionResult.WRONG_OUTPUT