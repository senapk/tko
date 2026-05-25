import signal
from typing import Any

from tko.util.rt import RT
from tko.util.raw_terminal import RawTerminal
from tko.util.runner import Runner
from tko.play.images import compilling_image
from tko.run.solver_builder import SolverBuilder
from tko.i18n import Msg, t
import subprocess
import random
import sys
import os


from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window


def ask() -> str:
    kb = KeyBindings()
    result: str = ""

    @kb.add("escape")
    def _(event: Any) -> None:
        nonlocal result
        result = "esc"
        event.app.exit()

    @kb.add("enter")
    def _(event: Any) -> None:
        nonlocal result
        result = "enter"
        event.app.exit()

    app: Any = Application(
        layout=Layout(Window()),
        key_bindings=kb,
        full_screen=False,
    )

    app.run()

    return result

_FREERUN_PROMPT_RERUN = Msg(
    pt="Para recompilar e reexecutar pressione ENTER",
    en="Press enter to recompile and rerun",
)
_FREERUN_PROMPT_BACK = Msg(
    pt="Para voltar para tela anterior pressione ESC",
    en="To go back, press ESC",
)

class Free:
    @staticmethod
    def free_run(solver: SolverBuilder, standalone_mode:bool=True, header: RT = RT()) -> bool:
        show_compilation = not standalone_mode
        to_clear = not standalone_mode
        wait_input = not standalone_mode

        if to_clear:
            Runner.clear_screen()
        if show_compilation:
            image = random.choice(list(compilling_image.keys()))
            for line in compilling_image[image].splitlines():
                print(RT(line, "y").center(RawTerminal.get_terminal_size(), " "))

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
                print(RT().center(RawTerminal.get_terminal_size(), "─"))
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
            print(RT().center(RawTerminal.get_terminal_size(), "─"))
            print(RT.parse(t(_FREERUN_PROMPT_RERUN)))
            print(RT.parse(t(_FREERUN_PROMPT_BACK)))

            valor = ask()
            if valor != "esc":
                if to_clear:
                    Runner.clear_screen()
                to_run_again = True
        if to_clear:
            Runner.clear_screen()

        return to_run_again
