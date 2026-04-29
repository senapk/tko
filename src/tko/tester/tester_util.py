import os

from tko.enums.diff_mode import DiffMode
from tko.enums.execution_result import ExecutionResult
from tko.game.task import Task
from tko.run.wdir import Wdir
from tko.util.rtext import RText
from tko.util.symbols import Symbols


def get_token(result: ExecutionResult) -> RText:
    if result == ExecutionResult.SUCCESS:
        return RText(ExecutionResult.get_symbol(ExecutionResult.SUCCESS).plain(), "G")
    if result == ExecutionResult.WRONG_OUTPUT:
        return RText(ExecutionResult.get_symbol(ExecutionResult.WRONG_OUTPUT).plain(), "R")
    if result == ExecutionResult.COMPILATION_ERROR:
        return RText(ExecutionResult.get_symbol(ExecutionResult.UNTESTED).plain(), "X")
    if result == ExecutionResult.EXECUTION_ERROR:
        return RText(ExecutionResult.get_symbol(ExecutionResult.EXECUTION_ERROR).plain(), "Y")
    return RText(ExecutionResult.get_symbol(ExecutionResult.UNTESTED).plain(), "X")


def get_diff_symbol(diff_mode: DiffMode) -> str:
    if diff_mode == DiffMode.DOWN:
        return Symbols.arrow_down
    return Symbols.arrow_right


def get_time_limit_symbol(timeout: int) -> str:
    if timeout == 0:
        return Symbols.infinity
    return str(timeout)


def get_folder(task: Task) -> str:
    folder = task.get_workspace_folder()
    if folder is None:
        raise Warning("Warning: Task folder não encontrado")
    return os.path.basename(folder)


def get_solver_names(wdir: Wdir) -> list[str]:
    return sorted(wdir.solvers_names())
