import subprocess
from subprocess import PIPE
from typing import List, Tuple, Any


class Runner:
    def __init__(self):
        pass

    @staticmethod
    def subprocess_run(cmd: str, input_data: str="") -> Tuple[int, Any, Any]:
        try:
            answer = subprocess.run(cmd, shell=True, check=True, input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return 0, answer.stdout, answer.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr

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
