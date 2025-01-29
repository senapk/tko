from .unit import Unit
from ..util.consts import ExecutionResult

from ..util.runner import Runner
from .solver_builder import SolverBuilder
from typing import Optional

class UnitRunner:

    def __init__(self):
        pass

    # run a unit using a solver and return if the result is correct
    @staticmethod
    def run_unit(solver: SolverBuilder, unit: Unit, timeout: Optional[float]=None) -> ExecutionResult:
        if solver.compile_error:
            unit.received = solver.error_msg
            return ExecutionResult.COMPILATION_ERROR
        cmd, folder = solver.get_executable()
        if timeout == 0:
            timeout = None

        return_code, stdout, stderr = Runner.subprocess_run(cmd, unit.inserted, timeout, folder)
        unit.received = stdout + stderr
        if return_code != 0:
            return ExecutionResult.EXECUTION_ERROR
        if unit.received == unit.expected:
            return ExecutionResult.SUCCESS
        return ExecutionResult.WRONG_OUTPUT