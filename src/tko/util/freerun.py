import subprocess
from .text import Text, Token
from .raw_terminal import RawTerminal
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
                print(Text().addf("y", line).center(RawTerminal.get_terminal_size(), Token(" ")))

        if show_compilling:
            Runner.clear_screen()
        solver.prepare_exec(free_run_mode=True)
        if solver.compile_error:
            print(solver.error_msg)
        else:
            cmd = solver.get_executable()
            print(Text().center(RawTerminal.get_terminal_size(), Token("─")))
            answer = subprocess.run(cmd, shell=True, text=True)
            if answer.returncode != 0 and answer.returncode != 1:
                print(Runner.decode_code(answer.returncode))
        solver.reset()
        to_run_again = False
        if wait_input:
            print(Text().center(RawTerminal.get_terminal_size(), Token("─")))
            print(Text().addf("y", "Deseja compilar e executar novamente? [").addf("c", "S").addf("y", "/n]: "), end="")
            valor = input()
            if valor != "n" and valor != "q":
                if to_clear:
                    Runner.clear_screen()
                to_run_again = True
        if to_clear:
            Runner.clear_screen()

        return to_run_again