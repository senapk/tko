from pathlib import Path
from tko.enums.diff_mode import DiffMode
from tko.enums.execution_result import ExecutionResult
from tko.game.task import Task
from tko.run.wdir import Wdir
from tko.util.rt import RT
from tko.util.symbols import Symbols
from tko.i18n import Msg


_TESTER_TASK_FOLDER_NOT_FOUND = Msg(
    pt="Warning: Pasta da tarefa não encontrada",
    en="Warning: Task folder not found",
)


def get_token(result: ExecutionResult) -> RT:
    if result == ExecutionResult.SUCCESS:
        return RT(ExecutionResult.get_symbol(ExecutionResult.SUCCESS).plain(), "G")
    if result == ExecutionResult.WRONG_OUTPUT:
        return RT(ExecutionResult.get_symbol(ExecutionResult.WRONG_OUTPUT).plain(), "R")
    if result == ExecutionResult.COMPILATION_ERROR:
        return RT(ExecutionResult.get_symbol(ExecutionResult.UNTESTED).plain(), "X")
    if result == ExecutionResult.EXECUTION_ERROR:
        return RT(ExecutionResult.get_symbol(ExecutionResult.EXECUTION_ERROR).plain(), "Y")
    return RT(ExecutionResult.get_symbol(ExecutionResult.UNTESTED).plain(), "X")


def get_diff_symbol(diff_mode: DiffMode) -> str:
    if diff_mode == DiffMode.DOWN:
        return Symbols.arrow_down
    return Symbols.arrow_right


def get_time_limit_symbol(timeout: int) -> str:
    if timeout == 0:
        return Symbols.infinity
    return str(timeout)


def get_folder(task: Task) -> Path:
    folder = task.path.work_dir
    if folder is None:
        raise Warning(str(_TESTER_TASK_FOLDER_NOT_FOUND))
    return folder


def get_solver_names(wdir: Wdir) -> list[str]:
    return sorted(wdir.solvers_names())
