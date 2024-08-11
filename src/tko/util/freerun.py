import subprocess
from typing import Tuple, Callable
import os
from subprocess import PIPE
from .sentence import Sentence, Token
from .term_color import term_print
from ..run.report import Report
from ..play.images import compilling
from .runner import Runner
from ..run.solver import Solver
import random

class Free:
    @staticmethod
    def free_run(solver: Solver, show_compilling:bool=True, to_clear: bool=True, wait_input:bool=True) -> bool:
        if to_clear:
            Runner.clear_screen()
        if show_compilling:
            image = random.choice(list(compilling.keys()))
            for line in compilling[image].split("\n"):
                term_print(Report.centralize(Sentence().addf("y", line), Token(" ")))

        if show_compilling:
            Runner.clear_screen()
        solver.prepare_exec()
        if solver.compile_error:
            print(solver.error_msg)
        else:
            cmd = solver.get_executable()
            term_print(Report.centralize(Sentence() + " " + cmd + " ", "─"))
            if cmd.startswith("node"):
                if os.name == "nt":
                    term_print(Report.centralize(Sentence() + " Use Control-Z Enter caso precise finalizar a entrada ", "─"))
                else:
                    term_print(Report.centralize(Sentence() + " Use Control-D caso precise finalizar a entrada ", "─"))
                
            answer = subprocess.run(cmd, shell=True, text=True)
            if answer.returncode != 0 and answer.returncode != 1:
                print(Runner.decode_code(answer.returncode))
            
        if wait_input:
            term_print(Report.centralize("", "─"))
            term_print(Sentence().addf("y", "Pressione (Enter) para executar novamente ou (q Enter) para sair: "), end="")
            valor = input()
            if valor != "q":
                if to_clear:
                    Runner.clear_screen()
                return True
        if to_clear:
            Runner.clear_screen()
        return False