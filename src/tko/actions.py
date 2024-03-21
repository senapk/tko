from typing import List, Optional
import os
import shutil

from .wdir import Wdir
from .basic import DiffMode, ExecutionResult, CompilerError, Param, Unit
from .diff import Diff
from .format import Colored, Color, Report, symbols
from .writer import Writer
from .solver import Solver
from .runner import Runner
from .filter import Filter


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

class Actions:

    def __init__(self):
        pass

    @staticmethod
    def deep_filter_copy(source, destiny, deep: int):
        if deep == 0:
            return
        if os.path.isdir(source):
            chain = source.split(os.sep)
            if len(chain) > 1 and chain[-1].startswith("."):
                return
            if not os.path.isdir(destiny):
                os.makedirs(destiny)
            for file in sorted(os.listdir(source)):
                Actions.deep_filter_copy(os.path.join(source, file), os.path.join(destiny, file), deep - 1)
        else:
            filename = os.path.basename(source)
            text_extensions = [".md", ".c", ".cpp", ".h", ".hpp", ".py", ".java", ".js", ".ts", ".hs"]

            if not any([filename.endswith(ext) for ext in text_extensions]):
                # shutil.copy(source, destiny)
                # print("(--------): " + destiny)
                return
            content = open(source, "r").read()
            processed = Filter(filename).process(content)
            with open(destiny, "w") as f:
                if processed != content:
                    print("(filtered): ", end="")
                else:
                    print("(        ): ", end="")
                f.write(processed)
                print(destiny)

    @staticmethod
    def filter_mode():
        # path to ~/.tko_filter
        filter_path = os.path.join(os.path.expanduser("~"), ".tko_filter")
        try:
            if not os.path.isdir(filter_path):
                os.makedirs(filter_path)
            else:
                # force remove  non empty dir
                shutil.rmtree(filter_path)
                os.makedirs(filter_path)
        except FileExistsError as e:
            print("fail: Dir " + filter_path + " could not be created.")
            print("fail: verify your permissions, or if there is a file with the same name.")
        
        Actions.deep_filter_copy(".", filter_path, 5)

        os.chdir(filter_path)



    @staticmethod
    def run(target_list: List[str], exec_cmd: Optional[str], param: Param.Basic) -> int:
        
        # modo de filtragem, antes de processar os dados, copiar tudo para o diretório temp fixo
        # filtrar os solvers para então continuar com a execução
        if param.filter:
            Actions.filter_mode()
            # change current directory to the filter directory
            

        try:
            wdir = Wdir().set_target_list(target_list).set_cmd(exec_cmd).build().filter(param)
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
            print(Report.centralize(" No solvers found. Listing Test Cases ", "╌"), flush=True)
            print(wdir.resume())
            print(wdir.unit_list_resume())
            return

        if wdir.solver is not None and len(wdir.unit_list) == 0:
            print(Report.centralize(" No test cases found. Running: " + wdir.solver.executable + " ", symbols.hbar), flush=True)
            # force print to terminal

            Runner.free_run(wdir.solver.executable)
            return
        
        print(Report.centralize(" Running solver against test cases ", "═"))

        ## print top line
        print(wdir.resume(), end="")
        print(" [", end="", flush=True)
        first = True
        for unit in wdir.unit_list:
            if first:
                first = False
            else:
                print(" ", end="", flush=True)
            unit.result = Execution.run_unit(wdir.solver, unit)
            print(ExecutionResult.get_symbol(unit.result), end="", flush=True)
        print("]")

        if param.diff_mode == DiffMode.QUIET:
            return
        
        results = [unit.result for unit in wdir.unit_list]
        if not ExecutionResult.EXECUTION_ERROR in results and not ExecutionResult.WRONG_OUTPUT in results:
            return
        
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
