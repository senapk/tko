from tko.run.unit import Unit
from tko.enums.execution_result import ExecutionResult
from tko.util.runner import Runner
from tko.run.solver_builder import SolverBuilder

class UnitRunner:

    def __init__(self):
        pass

    # run a unit using a solver and return if the result is correct
    @staticmethod
    def run_unit(solver: SolverBuilder, unit: Unit, timeout: None | float = None) -> ExecutionResult:
        executable, _ = solver.get_executable()
        if solver.has_compile_error():
            unit.set_received(executable.get_error_msg().get_str())
            return ExecutionResult.COMPILATION_ERROR
        cmd, folder = executable.get_command()
        if folder == "":
            folder = None
        if timeout == 0:
            timeout = None
        return_code, stdout, stderr = Runner.subprocess_run(cmd, unit.inserted, timeout, folder)
        if return_code != 0:
            unit.set_received(stdout + stderr)
            return ExecutionResult.EXECUTION_ERROR
        unit.set_received(stdout)
        if unit.get_received() == unit.get_expected():
            return ExecutionResult.SUCCESS
        return ExecutionResult.WRONG_OUTPUT
