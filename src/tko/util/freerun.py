import signal
from typing import Any

from tko.util.text import Text
from tko.util.raw_terminal import RawTerminal
from tko.util.runner import Runner
from tko.play.images import compilling_image
from tko.run.solver_builder import SolverBuilder
import subprocess
import random
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
    def free_run(solver: SolverBuilder, show_compilation:bool=True, to_clear: bool=True, wait_input:bool=True, header: Text = Text()) -> bool:

        if to_clear:
            Runner.clear_screen()
        if show_compilation:
            image = random.choice(list(compilling_image.keys()))
            for line in compilling_image[image].splitlines():
                print(Text().addf("y", line).center(RawTerminal.get_terminal_size(), Text.Token(" ")))

        if show_compilation:
            Runner.clear_screen()
        solver.prepare_exec()
        if solver.has_compile_error():
            executable, _ = solver.get_executable()
            print(executable.get_error_msg())
        else:
            executable, _ = solver.get_executable()
            cmd, folder = executable.get_command()
            if header.len() == 0:
                print(Text().center(RawTerminal.get_terminal_size(), Text.Token("─")))
            else:
                print(header.center(RawTerminal.get_terminal_size(), Text.Token("─")))

            kwargs: dict[str, Any] = {
                "cwd": folder,
                "shell": isinstance(cmd, str),
                "text": True,
            }

            if sys.platform != "win32":
                kwargs["preexec_fn"] = os.setsid
            else:
                kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

            answer = subprocess.Popen(cmd, **kwargs)
            #answer = subprocess.Popen(cmd, cwd=folder, shell=True if isinstance(cmd, str) else False, text=True, preexec_fn=os.setsid)
            try:
                answer.wait()
            except KeyboardInterrupt:
                answer.kill()
                os.killpg(os.getpgid(answer.pid), signal.SIGTERM)
            if answer.returncode != 0 and answer.returncode != 1:
                print(Runner.decode_code(answer.returncode))
        solver.reset()
        to_run_again = False
        if wait_input:
            while input_available():
                read_input()
            print(Text().center(RawTerminal.get_terminal_size(), Text.Token("─")))
            print(Text.format("Para [recompilar e] reexecutar pressione {y}", "enter"))
            print(Text.format("Para voltar para tela anterior digite {y} e pressione {y}", "q", "enter"))
            # clear buffer before get input

            valor = input()
            if valor != "n" and valor != "q":
                if to_clear:
                    Runner.clear_screen()
                to_run_again = True
        if to_clear:
            Runner.clear_screen()

        return to_run_again
