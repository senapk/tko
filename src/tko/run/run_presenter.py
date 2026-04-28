from tko.util.text import Text
from tko.util.raw_terminal import RawTerminal
from tko.enums.execution_result import ExecutionResult
from tko.enums.diff_count import DiffCount
from tko.enums.diff_mode import DiffMode
from tko.run.diff_builder_down import DiffBuilderDown
from tko.run.diff_builder_side import DiffBuilderSide
from tko.run.run_context import RunContext

class RunPresenter:
    def __init__(self, ctx: RunContext):
        self.ctx = ctx

    def print_diff(self):
        if self.ctx.wdir.get_solver().has_compile_error():
            executable, _ = self.ctx.wdir.get_solver().get_executable()
            print(executable.get_error_msg())
            return
        
        results = [unit.result for unit in self.ctx.wdir.get_unit_list()]
        if ExecutionResult.EXECUTION_ERROR not in results and ExecutionResult.WRONG_OUTPUT not in results:
            return
        
        if not self.ctx.param.compact:
            for elem in self.ctx.wdir.unit_list_resume():
                print(elem)

        if self.ctx.param.diff_count == DiffCount.NONE:
            return
        
        if self.ctx.param.diff_count == DiffCount.FIRST:
            wrong = [unit for unit in self.ctx.wdir.get_unit_list() if unit.result != ExecutionResult.SUCCESS][0]
            self._print_diff_for_unit(wrong)
            return

        if self.ctx.param.diff_count == DiffCount.ALL:
            for unit in self.ctx.wdir.get_unit_list():
                if unit.result != ExecutionResult.SUCCESS:
                    self._print_diff_for_unit(unit)

    def _print_diff_for_unit(self, unit):
        if self.ctx.param.diff_mode == DiffMode.DOWN:
            ud_diff_builder = DiffBuilderDown(RawTerminal.get_terminal_size(), unit).to_insert_header()
            for line in ud_diff_builder.build_diff():
                print(line)
        else:
            ss_diff_builder = DiffBuilderSide(RawTerminal.get_terminal_size(), unit).to_insert_header(True)
            for line in ss_diff_builder.build_diff():
                print(line)

    def list_mode(self):
        if not self.ctx.eval_mode:
            print(Text.format("Nenhum arquivo de código encontrado. Listando casos de teste.").center(RawTerminal.get_terminal_size(), Text.Token("╌")), flush=True)
        print(self.ctx.wdir.resume_splitted())
        for line in self.ctx.wdir.unit_list_resume():
            print(line)
