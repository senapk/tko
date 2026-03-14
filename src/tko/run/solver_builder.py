import tempfile

import os
import shutil
from tko.util.text import Text
from tko.util.runner import Runner
from tko.util.decoder import Decoder
import yaml #type: ignore
import io
from pathlib import Path

class CompileError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message

class Executable:
    def __init__(self, cmd: list[str] | None = None, files: list[Path] | None =  None, folder: str | None= None):
        if cmd is None:
            cmd = []
        if files is None:
            files = []
        self.__cmd_list: list[str] = cmd
        self.__folder: str | None = folder
        self.__compiled: bool = False
        self.__compile_error: bool = False
        self.__error_msg: Text = Text()
        self.need_shell_mode: bool = False # subprocess needs bash mode to process symbols like & or |
    
    def set_executable(self, cmd: list[str], files: list[Path], folder: str | None = None):
        self.__compiled = True
        self.__cmd_list = cmd
        self.__files = files
        self.__folder = folder
        return self
    
    def get_command(self) -> tuple[list[str], str | None]:
        cmd: list[str] | str = self.__cmd_list
        if isinstance(cmd, str):
            cmd += " " + " ".join([file.name for file in self.__files])
        else:
            cmd += [file.name for file in self.__files]
        return cmd, self.__folder

    def set_compile_error(self, error_msg: Text | str):
        self.__compiled = True
        self.__compile_error = True
        if isinstance(error_msg, str):
            self.__error_msg = Text().add(error_msg)
        else:
            self.__error_msg = error_msg
        return self
    
    def compiled(self):
        return self.__compiled

    def has_compile_error(self):
        return self.__compiled and self.__compile_error
    
    def get_error_msg(self):
        return self.__error_msg

class SolverBuilder:
    def __init__(self, args_list: list[Path]):
        self.args_list: list[Path] = args_list
        self.cache_dir: Path = Path()
        if len(self.args_list) > 0:
            self.cache_dir = self.args_list[0].parent / ".build"
        else:
            self.cache_dir = Path(tempfile.mkdtemp())
        self.clear_cache()
        self.__exec: Executable = Executable()

    def check_tool(self, name: str):
        if shutil.which(name) is None:
            self.__exec.set_compile_error(Text.format("{r}: O comando '" + name + "' não foi encontrado", "Falha")) 
            raise CompileError("fail: comando '" + name + "' não foi encontrado")

    def not_compiled(self):
        return not self.__exec.compiled()

    def has_compile_error(self):
        return self.__exec.has_compile_error()

    def set_main(self, main: str):
        list_main: list[Path] = []
        list_other: list[Path] = []

        for path in self.args_list:
            if path.name == main:
                list_main.append(path)
            else:
                list_other.append(path)

        self.args_list = list_main + list_other
        return self

    def clear_cache(self):
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir, ignore_errors=True)
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_executable(self, force_rebuild: bool = False) -> tuple[Executable, bool]:
        if not self.args_list:
            return Executable(), False
        if self.__exec.has_compile_error():
            return self.__exec, False
        if not self.__exec.compiled() or force_rebuild:
            self.prepare_exec()
        return self.__exec, True

    def reset(self):
        self.__exec = Executable()
        self.clear_cache()

    def prepare_exec(self, free_run_mode: bool = False) -> None:
        self.reset()
        first = self.args_list[0]

        if first.suffix == ".py":
            self.__prepare_python()
        elif first.suffix == ".yaml":
            self.__prepare_yaml()
        elif first.suffix == ".mk":
            self.__prepare_make()
        elif first.suffix == ".js":
            self.__prepare_js()
        elif first.suffix == ".ts":
            self.__prepare_ts(free_run_mode)
        elif first.suffix == ".java":
            self.__prepare_java()
        elif first.suffix == ".hs":
            self.__prepare_hs()
        elif first.suffix == ".c" or first.suffix == ".h":
            self.__prepare_c()
        elif first.suffix == ".cpp" or first.suffix == ".hpp":
            self.__prepare_cpp()
        elif first.suffix == ".go":
            self.__prepare_go()
        else:
            self.__exec.set_executable([str(x) for x in self.args_list], [], "")

    def __prepare_python(self):
        cmd_name = "python3"
        if shutil.which(cmd_name) is None:
            cmd_name = "python"
        self.__exec.set_executable([cmd_name], self.args_list, "")

    def __prepare_java(self):
        self.check_tool("javac")

        first = self.args_list[0]

        filename = first.name
        cmd: list[str] = ["javac"] + [str(x) for x in self.args_list] + ['-d', str(self.cache_dir)]
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        if return_code != 0:
            self.__exec.set_compile_error(stdout + stderr)
        else:
            self.__exec.set_executable(["java", "-cp"], [self.cache_dir / filename[:-5]])  # removing the .java

    def update_input_function(self, free_run_mode: bool, path_list: list[Path], copy_dir: Path):
        new_files: list[str] = []
        for origin in self.args_list:
            new_files.append(os.path.join(copy_dir, os.path.basename(origin)))

        for i in range(len(path_list)):
            origin = path_list[i]
            destiny = new_files[i]

            content = Decoder.load(origin)
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
        solver = os.path.abspath(self.args_list[0])
        folder = os.path.dirname(solver)
        content = Decoder.load(solver)
        yaml_data = yaml.safe_load(content)
        self.__exec.need_shell_mode = True

        if "build" in yaml_data and yaml_data["build"] is not None:
            build_txt = yaml_data["build"]
            if not isinstance(build_txt, str):
                raise Warning(Text.format("{r}: O campo build deve ser uma string", "Falha"))
            
            return_code, stdout, stderr = Runner.subprocess_run(build_txt, folder = folder)
            if return_code != 0:
                self.__exec.set_compile_error(stdout + stderr)
                return
        if not "run" in yaml_data:
            raise Warning(Text.format("{r}: Seu arquivo yaml precisa ter um campo {g} ", "Falha", "run:"))
        if not isinstance(yaml_data["run"], str):
            raise Warning(Text.format("{r}: O campo run deve ser uma lista", "Falha"))
        self.__exec.set_executable(yaml_data["run"], [], folder)

    def __prepare_make(self):
        self.check_tool("make")
        solver = os.path.abspath(self.args_list[0])
        folder = os.path.dirname(solver)
        cmd = ["make", "-s", "-C", folder, "-f", solver, "build"]
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        if return_code != 0:
            self.__exec.set_compile_error(stdout + stderr)
        else:
            self.__exec.set_executable(["make", "-s", "-C", folder, "-f", solver, "run"], [])

    def __prepare_js(self):
        self.check_tool("node")
        self.__exec.set_executable(["node"], self.args_list)

    def __prepare_go(self):
        self.check_tool("go")
        cache_exec = self.cache_dir / "main"
        cmd: list[str] = ["go", "build", "-o", str(cache_exec)] + [str(x) for x in self.args_list]
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        if return_code != 0:
            self.__exec.set_compile_error(stdout + stderr)
        else:
            self.__exec.set_executable([str(cache_exec)], [])

    def __prepare_ts(self, free_run_mode: bool):
        copy_dir = self.cache_dir / "src"
        # remove the cache dir
        if os.path.exists(copy_dir):
            shutil.rmtree(copy_dir, ignore_errors=True)
        os.makedirs(copy_dir, exist_ok=True)
        new_files = self.update_input_function(free_run_mode, self.args_list, copy_dir)
        transpiler = "npx"
        if os.name == "nt":
            transpiler += ".cmd"

        new_files = [os.path.abspath(x) for x in new_files]

        self.check_tool(transpiler)
        self.check_tool("node")
        transpiler = ["npx", "esbuild"]
        cmd: list[str] = transpiler + new_files + ["--outdir=" + str(self.cache_dir), "--format=cjs", "--log-level=error"]
        return_code, stdout, stderr = Runner.subprocess_run(cmd)

        if return_code != 0:
            self.__exec.set_compile_error(stdout + stderr)
        else:
            new_source_list: list[Path] = []
            for source in new_files:
                new_source_list.append(self.cache_dir / (os.path.basename(source)[:-2] + "js"))
            self.__exec.set_executable(cmd=["node"], files=new_source_list)  # renaming solver to main

    def __prepare_c_cpp(self, pre_args: list[str], pos_args: list[str]):
        source_list = [x for x in self.args_list if not x.suffix == ".h" and not x.suffix == ".hpp"]
        exec_path = self.cache_dir / ".a.out"
        cmd: list[str] = pre_args + [str(x) for x in source_list] + ["-o", str(exec_path)] + pos_args
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        if return_code != 0:
            self.__exec.set_compile_error(stdout + stderr)
        else:
            self.__exec.set_executable([], [exec_path])

    def __prepare_hs(self):
        self.check_tool("runhaskell")
        self.check_tool("ghc")
        self.__exec.set_executable(["runhaskell"], self.args_list, "")


    def __prepare_c(self):
        self.check_tool("gcc")
        pre = ["gcc", "-Wall"]
        pos = ["-lm"]
        self.__prepare_c_cpp(pre, pos)

    def __prepare_cpp(self):
        self.check_tool("g++")
        pre = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-Wno-deprecated"]
        pos: list[str] = []
        self.__prepare_c_cpp(pre, pos)
