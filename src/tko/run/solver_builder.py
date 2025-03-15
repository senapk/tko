import tempfile

import os
from typing import List
import shutil
from tko.util.text import Text
from tko.util.runner import Runner
from tko.util.decoder import Decoder
import yaml #type: ignore
import io

class CompileError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class SolverBuilder:
    def __init__(self, solver_list: List[str]):
        self.path_list: List[str] = [os.path.normpath(SolverBuilder.__add_dot_bar(path)) for path in solver_list]

        if len(self.path_list) > 0:
            self.cache_dir = os.path.join(os.path.dirname(self.path_list[0]), ".build")
        else:
            self.cache_dir = tempfile.mkdtemp()
        self.clear_cache()
        self.error_msg: str = ""
        self.__executable: tuple[str, str | None] = ("", None) # executavel e pasta
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

    def set_executable(self, executable: str, folder: str | None = None):
        self.__executable = (executable, folder)
        return self

    def clear_cache(self):
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)

    def reset(self):
        self.__executable = ("", None)
        self.compile_error = False
        self.error_msg = ""
        self.clear_cache()

    def not_compiled(self):
        cmd, folder = self.__executable
        return cmd == "" and not self.compile_error

    def get_executable(self, force_rebuild=False) -> tuple[str, str | None]:
        if (len(self.path_list) > 0 and self.not_compiled()) or force_rebuild:
            self.prepare_exec()
        cmd, folder = self.__executable
        return (cmd, None if folder == "" else folder)

    def prepare_exec(self, free_run_mode: bool = False) -> None:
        self.set_executable("")
        path = self.path_list[0]
        self.compile_error = False

        if path.endswith(".py"):
            self.set_executable("python " + path)
        elif path.endswith(".yaml"):
            self.__prepare_yaml()
        elif path.endswith(".mk"):
            self.__prepare_make()
        elif path.endswith(".js"):
            self.__prepare_js(free_run_mode)
        elif path.endswith(".ts"):
            self.__prepare_ts(free_run_mode)
        elif path.endswith(".java"):
            self.__prepare_java()
        elif path.endswith(".c") or path.endswith(".h"):
            self.__prepare_c()
        elif path.endswith(".cpp") or path.endswith(".hpp"):
            self.__prepare_cpp()
        elif path.endswith(".go"):
            self.__prepare_go()
        # elif path.endswith(".sql"):
        #     self.__prepare_sql()
        else:
            self.set_executable(path)

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
            self.set_executable("java -cp " + self.cache_dir + " " + filename[:-5])  # removing the .java

    def update_input_function(self, free_run_mode: bool, path_list: list[str], copy_dir: str):
        new_files: list[str] = []
        for origin in self.path_list:
            new_files.append(os.path.join(copy_dir, os.path.basename(origin)))

        for i in range(len(path_list)):
            origin = path_list[i]
            destiny = new_files[i]

            encoding = Decoder.get_encoding(origin)
            with open(origin, "r", encoding=encoding) as f:
                content = f.read()
                lines = content.splitlines(keepends=True)

            io_source = io.StringIO()
            io_target = io.StringIO()

            tag = "function input()"
            tag2 = "constinput=()=>"

            if free_run_mode:
                input_cmd = r'function input(): string { let X: any = input; X.P = X.P || require("readline-sync"); return X.P.question(); }'
                input_tag = 'const input = () => ""; // INTERATIVO\n'
            else:
                input_cmd = r'function input(): string { let X: any = input; X.L = X.L || require("fs").readFileSync(0).toString().split(/\r?\n/); return X.L.shift(); } '
                input_tag = 'const input = () => ""; // MODO_TESTE\n'

            inserted: bool = False
            for line in lines:
                match = False
                if not inserted:
                    filtered = "".join([c for c in line if c != " "])
                    match = filtered.startswith(tag2) or line.startswith(tag)
                if match:
                    inserted = True
                    io_source.write(input_tag)
                    io_target.write(input_cmd)
                else:
                    io_source.write(line)
                    io_target.write(line)

            result = io_source.getvalue()
            if result != content:
                with open(origin, "w", encoding="utf-8") as f:
                    f.write(io_source.getvalue())
            with open(destiny, "w", encoding="utf-8") as f:
                f.write(io_target.getvalue())
            io_source.close()
            io_target.close()
        return new_files

    def __prepare_yaml(self):
        solver = os.path.abspath(self.path_list[0])
        folder = os.path.dirname(solver)
        content = Decoder.load(solver)
        yaml_data = yaml.safe_load(content)

        if "build" in yaml_data and yaml_data["build"] is not None:
            build_cmd = yaml_data["build"]
            return_code, stdout, stderr = Runner.subprocess_run(build_cmd, folder = folder)
            if return_code != 0:
                self.error_msg = stdout + stderr
                self.compile_error = True
                return
        if not "run" in yaml_data:
            raise Warning(Text.format("{r}: Seu arquivo yaml precisa ter um campo {g} ", "Falha", "run:"))
        self.set_executable(yaml_data["run"], folder)

    def __prepare_make(self):
        self.check_tool("make")
        solver = os.path.abspath(self.path_list[0])
        folder = os.path.dirname(solver)
        cmd = "make -s -C {} -f {} build".format(folder, solver)
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        if return_code != 0:
            self.error_msg = stdout + stderr
            self.compile_error = True
        else:
            self.set_executable("make -s -C {} -f {} run".format(folder, solver))

    def __prepare_js(self, free_run_mode: bool):
        self.check_tool("node")
        solver = self.path_list[0]
        self.set_executable("node " + solver)

    def __prepare_go(self):
        self.check_tool("go")
        self.set_executable("go run " + " ".join(self.path_list))

    # def __prepare_sql(self):
    #     self.check_tool("sqlite3")
    #     self.__executable = "cat " + " ".join(self.path_list) + " | sqlite3"

    def __prepare_ts(self, free_run_mode: bool):
        copy_dir = os.path.join(self.cache_dir, "src")
        # remove the cache dir
        if os.path.exists(copy_dir):
            shutil.rmtree(copy_dir)
        os.makedirs(copy_dir, exist_ok=True)
        new_files = self.update_input_function(free_run_mode, self.path_list, copy_dir)
        transpiler = "npx"
        if os.name == "nt":
            transpiler += ".cmd"

        self.check_tool(transpiler)
        self.check_tool("node")
        transpiler = "npx esbuild"
        cmd = [transpiler] + new_files + ["--outdir=" + self.cache_dir, "--format=cjs", "--log-level=error"]
        return_code, stdout, stderr = Runner.subprocess_run(" ".join(cmd))

        if return_code != 0:
            self.error_msg = stdout + stderr
            self.compile_error = True
        else:
            new_source_list = []
            for source in new_files:
                new_source_list.append(os.path.join(self.cache_dir, os.path.basename(source)[:-2] + "js"))
            self.set_executable("node " + " ".join(new_source_list))  # renaming solver to main

    def __prepare_c_cpp(self, pre_args: List[str], pos_args: List[str]):
        # solver = self.path_list[0]
        tempdir = self.cache_dir
        source_list = [x for x in self.path_list if not x.endswith(".h") and not x.endswith(".hpp")]

        # print("Using the following source files: " + str([os.path.basename(x) for x in source_list]))

        exec_path = os.path.join(tempdir, ".a.out")
        cmd = pre_args + source_list + ["-o", exec_path] + pos_args
        return_code, stdout, stderr = Runner.subprocess_run(" ".join(cmd))
        if return_code != 0:
            self.error_msg = stdout + stderr
            self.compile_error = True
        else:
            self.set_executable(exec_path)

    def __prepare_c(self):
        self.check_tool("gcc")
        pre = ["gcc", "-Wall"]
        pos = ["-lm"]
        self.__prepare_c_cpp(pre, pos)

    def __prepare_cpp(self):
        self.check_tool("g++")
        pre = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-Wno-deprecated"]
        pos: List[str] = []
        # fmt_lib = False
        # for path in self.path_list:
        #     if os.path.isfile(path):
        #         content = Decoder.load(path)
        #         if "#include <fmt" in content:
        #             fmt_lib = True
        #             break
        # if fmt_lib:
        #     pos.append("-lfmt")

        self.__prepare_c_cpp(pre, pos)

    @staticmethod
    def __add_dot_bar(solver: str) -> str:
        if os.sep not in solver and os.path.isfile("." + os.sep + solver):
            solver = "." + os.sep + solver
        return solver
