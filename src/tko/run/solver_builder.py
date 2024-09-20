import tempfile

import os
from typing import List
import shutil

from ..util.runner import Runner

class CompileError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class SolverBuilder:
    def __init__(self, solver_list: List[str]):
        self.path_list: List[str] = [os.path.normpath(SolverBuilder.__add_dot_bar(path)) for path in solver_list]
        
        if len(self.path_list) > 0:
            self.cache_dir = os.path.join(os.path.dirname(self.path_list[0]), ".cache")
        else:
            self.cache_dir = tempfile.mkdtemp()
        self.clear_cache()
        self.error_msg: str = ""
        self.__executable: str = ""
        self.compile_error: bool = False

    def check_tool(self, name):
        if shutil.which(name) is None:
            self.compile_error = True
            raise CompileError("fail: comando '" + name + "' não foi encontrado")

    def set_main(self, main: str):
        list_main: List[str] = []
        list_other: List[str] = []

        for path in self.path_list:
            if os.path.basename(path) == main:
                list_main.append(path)
            else:
                list_other.append(path)
        
        self.path_list = list_main + list_other
        return self

    def set_executable(self, executable: str):
        self.__executable = executable
        return self

    def clear_cache(self):
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)

    def reset(self):
        self.__executable = ""
        self.compile_error = False
        self.error_msg = ""
        self.clear_cache()

    def not_compiled(self):
        return self.__executable == "" and not self.compile_error

    def get_executable(self, force_rebuild=False) -> str:
        if (len(self.path_list) > 0 and self.not_compiled()) or force_rebuild:
            self.prepare_exec()
        return self.__executable

    def prepare_exec(self, free_run_mode: bool = False) -> None:
        self.__executable = ""
        path = self.path_list[0]
        self.compile_error = False

        if path.endswith(".py"):
            self.__executable = "python " + path
        elif path.endswith(".js"):
            self.__prepare_js(free_run_mode)
        elif path.endswith(".ts"):
            self.__prepare_ts(free_run_mode)
        elif path.endswith(".java"):
            self.__prepare_java()
        elif path.endswith(".c"):
            self.__prepare_c()
        elif path.endswith(".cpp"):
            self.__prepare_cpp()
        elif path.endswith(".go"):
            self.__prepare_go()
        elif path.endswith(".sql"):
            self.__prepare_sql()
        else:
            self.__executable = path

    def __prepare_java(self):
        self.check_tool("javac")

        solver = self.path_list[0]

        filename = os.path.basename(solver)
        # tempdir = os.path.dirname(self.path_list[0])

        cmd = ["javac"] + self.path_list + ['-d', self.cache_dir]
        cmdt = " ".join(cmd)
        return_code, stdout, stderr = Runner.subprocess_run(cmdt)
        if return_code != 0:
            self.error_msg = stdout + stderr
            self.compile_error = True
        else:
            self.__executable = "java -cp " + self.cache_dir + " " + filename[:-5]  # removing the .java

    def comment_and_uncomment_node_input(self, free_run_mode: bool):
        for i in range(len(self.path_list)):
            path = self.path_list[i]
            with open(path, "r") as f:
                lines = f.readlines()
            with open(path, "w") as f:
                for line in lines:
                    if free_run_mode:
                        if '_TEST_ONLY_' in line and not line.startswith("//"):
                            f.write("//" + line)
                        elif '_FREE_ONLY' in line and line.startswith("// function"):
                            f.write(line[3:])
                        elif '_FREE_ONLY' in line and line.startswith("//"):
                            f.write(line[2:])
                        else:
                            f.write(line)
                    else:
                        if '_FREE_ONLY_' in line and not line.startswith("//"):
                            f.write("//" + line)
                        elif '_TEST_ONLY' in line and line.startswith("// function"):
                            f.write(line[3:])
                        elif '_TEST_ONLY' in line and line.startswith("//"):
                            f.write(line[2:])
                        else:
                            f.write(line)

    def __prepare_js(self, free_run_mode: bool):
        self.check_tool("node")
        solver = self.path_list[0]
        self.comment_and_uncomment_node_input(free_run_mode)
        self.__executable = "node " + solver

    def __prepare_go(self):
        self.check_tool("go")
        self.__executable = "go run " + " ".join(self.path_list)

    def __prepare_sql(self):
        self.check_tool("sqlite3")
        self.__executable = "cat " + " ".join(self.path_list) + " | sqlite3"

    def __prepare_ts(self, free_run_mode: bool):
        self.comment_and_uncomment_node_input(free_run_mode)
        
        transpiler = "esbuild"
        if os.name == "nt":
            transpiler += ".cmd"

        self.check_tool(transpiler)
        self.check_tool("node")
        source_list = self.path_list
        cmd = [transpiler] + source_list + ["--outdir=" + self.cache_dir, "--format=cjs", "--log-level=error"]
        return_code, stdout, stderr = Runner.subprocess_run(" ".join(cmd))
        if return_code != 0:
            self.error_msg = stdout + stderr
            self.compile_error = True
        else:
            new_source_list = []
            for source in source_list:
                new_source_list.append(os.path.join(self.cache_dir, os.path.basename(source)[:-2] + "js"))
            self.__executable = "node " + " ".join(new_source_list)  # renaming solver to main
    
    def __prepare_c_cpp(self, pre_args: List[str], pos_args: List[str]):
        # solver = self.path_list[0]
        tempdir = self.cache_dir
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
        self.check_tool("gcc")
        pre = ["gcc", "-Wall"]
        pos = ["-lm"]
        self.__prepare_c_cpp(pre, pos)

    def __prepare_cpp(self):
        self.check_tool("g++")
        pre = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror"]
        pos: List[str] = []
        self.__prepare_c_cpp(pre, pos)

    @staticmethod
    def __add_dot_bar(solver: str) -> str:
        if os.sep not in solver and os.path.isfile("." + os.sep + solver):
            solver = "." + os.sep + solver
        return solver
    