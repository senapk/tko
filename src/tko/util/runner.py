import subprocess
import os
from subprocess import PIPE


class Runner:
    def __init__(self):
        pass

    @staticmethod
    def subprocess_run(cmd: str | list[str], input_data: str = "", timeout: None | float = None, folder: str | None = None, shell_mode: bool = False) -> tuple[int, str, str]:
        try:
            env = os.environ.copy()
            env['NO_COLOR'] = '1'
            env['FORCE_COLOR'] = '0'
            
            answer = subprocess.run(cmd, 
                                    cwd=folder, 
                                    env=env, 
                                    shell= True if isinstance(cmd, str) else False, 
                                    input=input_data, 
                                    stdout=PIPE, 
                                    stderr=PIPE, 
                                    timeout=timeout, 
                                    text=True
                                    )
            err = ""
            if answer.returncode != 0:
                err = answer.stderr + Runner.decode_code(answer.returncode)
            return answer.returncode, answer.stdout, err
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
    def decode_code(return_code: int) -> str:
        code = 128 - return_code
        if code == 127:
            return ""
        if code == 139:
            return "fail: segmentation fault"
        if code == 134:
            return "fail: runtime exception"
        return "fail: execution error code " + str(code)
