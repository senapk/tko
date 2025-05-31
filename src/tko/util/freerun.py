from tko.util.text import Text, Token, aprint
from tko.util.raw_terminal import RawTerminal
from tko.util.runner import Runner
from tko.play.images import compilling_image
from tko.run.solver_builder import SolverBuilder
import subprocess
import random
import select
import sys
import os

if os.name == 'nt':  # Windows
    import msvcrt

    def input_available():
        return msvcrt.kbhit()

    def read_input():
        return msvcrt.getwch()  # use getch() para byte
else:  # Unix (Linux, macOS)
    import select

    def input_available():
        return select.select([sys.stdin], [], [], 0)[0]

    def read_input():
        return sys.stdin.readline()

class Free:
    @staticmethod
    def free_run(solver: SolverBuilder, show_compilling:bool=True, to_clear: bool=True, wait_input:bool=True, header: Text = Text()) -> bool:

        if to_clear:
            Runner.clear_screen()
        if show_compilling:
            image = random.choice(list(compilling_image.keys()))
            for line in compilling_image[image].splitlines():
                aprint(Text().addf("y", line).center(RawTerminal.get_terminal_size(), Token(" ")))

        if show_compilling:
            Runner.clear_screen()
        solver.prepare_exec(free_run_mode=True)
        if solver.has_compile_error():
            exec, _ = solver.get_executable()
            aprint(exec.get_error_msg())
        else:
            exec, _ = solver.get_executable()
            cmd, folder = exec.get_command()
            if folder == "":
                folder = None
            if header.len() == 0:
                aprint(Text().center(RawTerminal.get_terminal_size(), Token("─")))
            else:
                aprint(header.center(RawTerminal.get_terminal_size(), Token("─")))
            answer = subprocess.run(cmd, cwd=folder, shell=True, text=True)
            if answer.returncode != 0 and answer.returncode != 1:
                aprint(Runner.decode_code(answer.returncode))
        solver.reset()
        to_run_again = False
        if wait_input:
            while input_available():
                read_input()
            aprint(Text().center(RawTerminal.get_terminal_size(), Token("─")))
            aprint(Text.format("Para [recompilar e] reexecutar digite: {y}", "<enter>"))
            aprint(Text.format("Para voltar para tela anterior digite: {y}", "q<enter>"))
            # clear buffer before get input

            valor = input()
            if valor != "n" and valor != "q":
                if to_clear:
                    Runner.clear_screen()
                to_run_again = True
        if to_clear:
            Runner.clear_screen()

        return to_run_again