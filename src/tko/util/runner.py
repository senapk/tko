from pathlib import Path
import subprocess
import os
from subprocess import PIPE

from tko.util.console import Console
from tko.util.rt import RT


class Runner:
    def __init__(self):
        pass

    @staticmethod
    def subprocess_run(cmd: str | list[str], input_data: str = "", timeout: None | float = None, folder: Path | None = None) -> tuple[int, str, str]:
        if os.name == 'nt':
            shell = True
        else:
            shell = isinstance(cmd, str)
        try:
            env = os.environ.copy()
            env['NO_COLOR'] = '1'
            env['FORCE_COLOR'] = '0'
            answer = subprocess.run(cmd, 
                                    cwd=folder, 
                                    env=env, 
                                    input=input_data, 
                                    stdout=PIPE, 
                                    stderr=PIPE, 
                                    timeout=timeout, 
                                    shell=shell,
                                    text=True,
                                    encoding="utf-8",
                                    )

            return answer.returncode, answer.stdout, answer.stderr
        except FileNotFoundError:
            err = "fail: comando não encontrado ({})".format(cmd if isinstance(cmd, str) else cmd[0])
            return 1, "", err
        except subprocess.TimeoutExpired:
            err = "fail: processo abortado depois de {} segundos".format(timeout)
            return 1, "", err

    @staticmethod
    def clear_screen():
        Console.stdout.write(RT("\033[2J\033[H"), end="")
        Console.stdout.flush()
