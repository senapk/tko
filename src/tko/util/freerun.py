import signal
from typing import Any

from tko.util.rtext import RText
from tko.util.raw_terminal import RawTerminal
from tko.util.runner import Runner
from tko.play.images import compilling_image
from tko.run.solver_builder import SolverBuilder
from tko.i18n import MsgKey, t
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
    def free_run(solver: SolverBuilder, standalone_mode:bool=True, header: RText = RText()) -> bool:
        show_compilation = not standalone_mode
        to_clear = not standalone_mode
        wait_input = not standalone_mode

        if to_clear:
            Runner.clear_screen()
        if show_compilation:
            image = random.choice(list(compilling_image.keys()))
            for line in compilling_image[image].splitlines():
                print(RText(line, "y").center(RawTerminal.get_terminal_size(), " "))

        if show_compilation:
            Runner.clear_screen()
        solver.prepare_exec()
        if solver.has_compile_error():
            executable, _ = solver.get_executable()
            print(executable.get_error_msg())
        else:
            executable, _ = solver.get_executable()
            cmd, folder = executable.get_command()
            if len(header) == 0:
                print(RText().center(RawTerminal.get_terminal_size(), "─"))
            else:
                print(header.center(RawTerminal.get_terminal_size(), "─"))

            kwargs: dict[str, Any] = {
                "cwd": folder,
                "shell": isinstance(cmd, str),
                "text": True,
            }
            if not standalone_mode:
                if sys.platform != "win32":
                    kwargs["preexec_fn"] = os.setsid
                else:
                    kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

                answer = subprocess.Popen(cmd, **kwargs)
                try:
                    answer.wait()
                except KeyboardInterrupt:
                    answer.kill()
                    os.killpg(os.getpgid(answer.pid), signal.SIGTERM)
                if answer.returncode != 0 and answer.returncode != 1:
                    print(Runner.decode_code(answer.returncode))
            else:
                subprocess.run(cmd, **kwargs)
                
        solver.reset()
        to_run_again = False
        if wait_input:
            while input_available():
                read_input()
            print(RText().center(RawTerminal.get_terminal_size(), "─"))
            print(RText.parse(t(MsgKey.FREERUN_PROMPT_RERUN)))
            print(RText.parse(t(MsgKey.FREERUN_PROMPT_BACK)))

            valor = input()
            if valor != "n" and valor != "q":
                if to_clear:
                    Runner.clear_screen()
                to_run_again = True
        if to_clear:
            Runner.clear_screen()

        return to_run_again
