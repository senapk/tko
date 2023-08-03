from .solver import Solver
from .unit import Unit
from .symbol import Symbol
from .enums import ExecutionResult
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

