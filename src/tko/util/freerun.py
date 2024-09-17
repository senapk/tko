import subprocess
from .sentence import Sentence, Token
from .term_color import term_print
from .report import Report
from ..play.images import compilling
from .runner import Runner
from ..run.solver_builder import SolverBuilder
import random

class Free:
    @staticmethod
    def free_run(solver: SolverBuilder, show_compilling:bool=True, to_clear: bool=True, wait_input:bool=True) -> bool:

        if to_clear:
            Runner.clear_screen()
        if show_compilling:
            image = random.choice(list(compilling.keys()))
            for line in compilling[image].split("\n"):
                term_print(Report.centralize(Sentence().addf("y", line), Token(" ")))

        if show_compilling:
            Runner.clear_screen()
        solver.prepare_exec(free_run_mode=True)
        if solver.compile_error:
            print(solver.error_msg)
        else:
            cmd = solver.get_executable()
            term_print(Report.centralize(Sentence(), "─"))
            answer = subprocess.run(cmd, shell=True, text=True)
            if answer.returncode != 0 and answer.returncode != 1:
                print(Runner.decode_code(answer.returncode))
        to_run_again = False
        if wait_input:
            term_print(Report.centralize("", "─"))
            term_print(Sentence().addf("y", "Deseja compilar e executar novamente? (").addf("c", "s").addf("y", "/n): "), end="")
            valor = input()
            if valor != "n" and valor != "q":
                if to_clear:
                    Runner.clear_screen()
                to_run_again = True
        if to_clear:
            Runner.clear_screen()

        return to_run_again