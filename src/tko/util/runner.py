import subprocess
from typing import Tuple, Optional
import os
from subprocess import PIPE

class Runner:
    def __init__(self):
        pass

    @staticmethod
    def subprocess_run(cmd: str, input_data: str = "", timeout:Optional[float] = None, folder: str | None = None) -> Tuple[int, str, str]:
        try:
            answer = subprocess.run(cmd, cwd=folder, shell=True, input=input_data, stdout=PIPE, stderr=PIPE, text=True, timeout=timeout)
            err = ""
            if answer.returncode != 0:
                err = answer.stderr + Runner.decode_code(answer.returncode)
            # if running on windows
            if os.name == "nt":
                return answer.returncode, answer.stdout.encode("cp1252").decode("utf-8"), err
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

# class Runner:

#     def __init__(self):
#         pass

#     @staticmethod
#     def subprocess_run(cmd_list: List[str], input_data: str = "") -> Tuple[int, Any, Any]:
#         try:
#             p = subprocess.Popen(cmd_list, stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
#             stdout, stderr = p.communicate(input=input_data)
#             return p.returncode, stdout, stderr
#         except FileNotFoundError:
#             print("\n\nCommand not found: " + " ".join(cmd_list))
#             exit(1)
