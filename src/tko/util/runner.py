from pathlib import Path
import subprocess
import os
from subprocess import PIPE


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
                                    text=True
                                    )

            err = ""
            if answer.returncode != 0:
                err = Runner.decode_code(answer.returncode)
            return answer.returncode, answer.stdout, err
        except FileNotFoundError:
            err = "fail: comando não encontrado ({})".format(cmd if isinstance(cmd, str) else cmd[0])
            return 1, "", err
        except subprocess.TimeoutExpired:
            err = "fail: processo abortado depois de {} segundos".format(timeout)
            return 1, "", err

    @staticmethod
    def clear_screen():
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def decode_code(return_code: int | None) -> str:
        # if return_code is None:
        #     return "fail: Process was killed"
        
        # # Linux shells may report signal exits as 128 + signal (e.g. 134),
        # # while subprocess may also expose them as negative signals (e.g. -6).
        # if return_code < 0:
        #     signal = -return_code
        # elif return_code >= 128:
        #     signal = return_code - 128
        # else:
        #     signal = None

        # if signal == 11:
        #     return "fail: segmentation fault"
        # if signal == 6:
        #     return "fail: runtime exception"
        return "fail: runtime exception"
