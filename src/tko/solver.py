import tempfile

import os
from typing import List

from .runner import Runner


class Solver:
    def __init__(self, solver_list: List[str]):
        self.path_list: List[str] = [Solver.__add_dot_bar(path) for path in solver_list]
        
        self.temp_dir = tempfile.mkdtemp()
        # print("Tempdir for execution: " + self.temp_dir)
        # copia para tempdir e atualiza os paths

        # new_paths = []
        # for path in self.path_list:
        #     if os.path.isfile(path):
        #         new_paths.append(shutil.copy(path, self.temp_dir))
        #     else:
        #         print("File not found: " + path)
        #         exit(1)
                
        # self.path_list = new_paths
        
        self.error_msg: str = ""
        self.executable: str = ""
        self.prepare_exec()

    def prepare_exec(self) -> None:
        path = self.path_list[0]

        if " " in path:  # more than one parameter
            self.executable = path
        elif path.endswith(".py"):
            self.executable = "python " + path
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
        else:
            self.executable = path

    def __prepare_java(self):
        solver = self.path_list[0]
        filename = os.path.basename(solver)
        tempdir = os.path.dirname(self.path_list[0])
        
        cmd = ["javac"] + self.path_list + ['-d', tempdir]
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        print(stdout)
        print(stderr)
        if return_code != 0:
            raise Runner.CompileError(stdout + stderr)
        # solver = solver.split(os.sep)[-1]  # getting only the filename
        self.executable = "java -cp " + tempdir + " " + filename[:-5]  # removing the .java

    def __prepare_js(self):
        import_str = (r'let __lines = require("fs").readFileSync(0).toString().split("\n"); let input = () => '
                      r'__lines.length === 0 ? "" : __lines.shift(); let write = (text, end="\n") => '
                      r'process.stdout.write("" + text + end);')
        solver = self.path_list[0]
        with open(solver, "r") as f:
            content = f.read()
        with open(solver, "w") as f:
            f.write(content.replace("let input,write", import_str))
        self.executable = "node " + solver

    def __prepare_ts(self):
        import_str = (r'let _cin_: string[] = require("fs").readFileSync(0).toString().split("\n"); let input = () : '
                      r'string => _cin_.length === 0 ? "" : _cin_.shift()!; let write = (text: any, '
                      r'end:string="\n")=> process.stdout.write("" + text + end);')
        solver = self.path_list[0]
        with open(solver, "r") as f:
            content = f.read()
        with open(solver, "w") as f:
            f.write(content.replace("let input,write", import_str))
        
        filename = os.path.basename(solver)
        source_list = self.path_list
        # print("Using the following source files: " + str([os.path.basename(x) for x in source_list]))
        # compile the ts file
        cmd = ["esbuild"] + source_list + ["--outdir=" + self.temp_dir, "--format=cjs", "--log-level=error"]
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        print(stdout + stderr)
        if return_code != 0:
            raise Runner.CompileError(stdout + stderr)
        jsfile = os.path.join(self.temp_dir, filename[:-3] + ".js")
        self.executable = "node " + jsfile  # renaming solver to main
    
    def __prepare_c_cpp(self, pre_args: List[str], pos_args: list[str]):
        # solver = self.path_list[0]
        tempdir = self.temp_dir
        source_list = self.path_list
        # print("Using the following source files: " + str([os.path.basename(x) for x in source_list]))
        
        exec_path = os.path.join(tempdir, ".a.out")
        cmd = pre_args + source_list + ["-o", exec_path] + pos_args
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        if return_code != 0:
            raise Runner.CompileError(stdout + stderr)
        self.executable = exec_path

    def __prepare_c(self):
        pre = ["gcc", "-Wall"]
        pos = ["-lm", "-lutil"]
        self.__prepare_c_cpp(pre, pos)

    def __prepare_cpp(self):
        pre = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror"]
        pos = []
        self.__prepare_c_cpp(pre, pos)

    @staticmethod
    def __add_dot_bar(solver: str) -> str:
        if os.sep not in solver and os.path.isfile("." + os.sep + solver):
            solver = "." + os.sep + solver
        return solver
    