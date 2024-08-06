import subprocess
from typing import Tuple
import os
from subprocess import PIPE
from .ftext import Sentence
from .term_color import term_print
from ..run.report import Report


class Runner:
    def __init__(self):
        pass

    @staticmethod
    def subprocess_run(cmd: str, input_data: str = "") -> Tuple[int, str, str]:
        answer = subprocess.run(cmd, shell=True, input=input_data, stdout=PIPE, stderr=PIPE, text=True)
        err = ""
        if answer.returncode != 0:
            err = answer.stderr + Runner.decode_code(answer.returncode)

        # if running on windows
        if os.name == "nt":
            return answer.returncode, answer.stdout.encode("cp1252").decode("utf-8"), err
        return answer.returncode, answer.stdout, err


    @staticmethod
    def clear_screen():
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def free_run(cmd: str, to_clear: bool=True, wait_input:bool=True) -> None:
        if to_clear:
            Runner.clear_screen()
        term_print(Report.centralize(Sentence() + " Rodando o código " + cmd + " ", "─"))
        term_print(Report.centralize(Sentence() + " Se necessário, digite Control D para finalizar a entrada ", "─"))

        answer = subprocess.run(cmd, shell=True, text=True)
        if answer.returncode != 0 and answer.returncode != 1:
            print(Runner.decode_code(answer.returncode))
        if wait_input:
            term_print(Report.centralize(Sentence() + " Digite enter para continuar ", "─"))
            input()

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
