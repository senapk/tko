import tempfile

import os
from typing import List
import shutil

from ..run.basic import CompilerError
from ..util.runner import Runner


def check_tool(name):
    if shutil.which(name) is None:
        raise CompilerError("fail: " + name + " executable not found")


class Solver:
    def __init__(self, solver_list: List[str]):
        self.path_list: List[str] = [os.path.normpath(Solver.__add_dot_bar(path)) for path in solver_list]
        
        self.temp_dir = tempfile.mkdtemp()
        self.error_msg: str = ""
        self.__executable: str = ""
        self.compile_error: bool = False

    def set_executable(self, executable: str) -> None:
        self.__executable = executable

    def get_executable(self) -> str:
        if len(self.path_list) > 0 and self.__executable == "":
            self.prepare_exec()
        return self.__executable

    def prepare_exec(self) -> None:
        path = self.path_list[0]

        if path.endswith(".py"):
            self.__executable = "python " + path
        elif path.endswith(".js"):
            self.__prepare_js()
        elif path.endswith(".ts"):
            self.__prepare_ts()
        elif path.endswith(".java"):
            self.__prepare_java()
        elif path.endswith(".c"):
            self.__prepare_c()
        elif path.endswith(".cpp"):
            self.__prepare_cpp()
        elif path.endswith(".sql"):
            self.__prepare_sql()
        else:
            self.__executable = path

    def __prepare_java(self):
        check_tool("javac")

        solver = self.path_list[0]

        filename = os.path.basename(solver)
        # tempdir = os.path.dirname(self.path_list[0])

        cmd = ["javac"] + self.path_list + ['-d', self.temp_dir]
        cmdt = " ".join(cmd)
        return_code, stdout, stderr = Runner.subprocess_run(cmdt)
        if return_code != 0:
            self.error_msg = stdout + stderr
            self.compile_error = True
        else:
            self.__executable = "java -cp " + self.temp_dir + " " + filename[:-5]  # removing the .java

    def __prepare_js(self):
        check_tool("node")
        solver = self.path_list[0]
        self.__executable = "node " + solver

    def __prepare_sql(self):
        check_tool("sqlite3")
        self.__executable = "cat " + " ".join(self.path_list) + " | sqlite3"

    def __prepare_ts(self):
        transpiler = "esbuild"
        if os.name == "nt":
            transpiler += ".cmd"

        check_tool(transpiler)
        check_tool("node")

        solver = self.path_list[0]

        filename = os.path.basename(solver)
        source_list = self.path_list
        cmd = [transpiler] + source_list + ["--outdir=" + self.temp_dir, "--format=cjs", "--log-level=error"]
        return_code, stdout, stderr = Runner.subprocess_run(" ".join(cmd))
        if return_code != 0:
            self.error_msg = stdout + stderr
            self.compile_error = True
        else:
            jsfile = os.path.join(self.temp_dir, filename[:-3] + ".js")
            self.__executable = "node " + jsfile  # renaming solver to main
    
    def __prepare_c_cpp(self, pre_args: List[str], pos_args: List[str]):
        # solver = self.path_list[0]
        tempdir = self.temp_dir
        source_list = self.path_list
        # print("Using the following source files: " + str([os.path.basename(x) for x in source_list]))
        
        exec_path = os.path.join(tempdir, ".a.out")
        cmd = pre_args + source_list + ["-o", exec_path] + pos_args
        return_code, stdout, stderr = Runner.subprocess_run(" ".join(cmd))
        if return_code != 0:
            self.error_msg = stdout + stderr
            self.compile_error = True
        else:
            self.__executable = exec_path

    def __prepare_c(self):
        check_tool("gcc")
        pre = ["gcc", "-Wall"]
        pos = ["-lm"]
        self.__prepare_c_cpp(pre, pos)

    def __prepare_cpp(self):
        check_tool("g++")
        pre = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror"]
        pos: List[str] = []
        self.__prepare_c_cpp(pre, pos)

    @staticmethod
    def __add_dot_bar(solver: str) -> str:
        if os.sep not in solver and os.path.isfile("." + os.sep + solver):
            solver = "." + os.sep + solver
        return solver
    