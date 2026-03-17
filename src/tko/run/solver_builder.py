import tempfile

import os
import shutil
from tko.util.text import Text
from tko.util.runner import Runner
from tko.settings.settings import Settings
import yaml #type: ignore
from pathlib import Path

class CompileError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message

class Executable:
    def __init__(self, cmd: list[str] | None = None, files: list[Path] | None =  None, folder: Path | None= None):
        if cmd is None:
            cmd = []
        if files is None:
            files = []
        self.__cmd_list: list[str] = cmd
        self.__folder: Path | None = folder
        self.__compiled: bool = False
        self.__compile_error: bool = False
        self.__error_msg: Text = Text()
        self.need_shell_mode: bool = False # subprocess needs bash mode to process symbols like & or |
    
    def set_executable(self, cmd: list[str], files: list[Path], folder: Path | None = None):
        self.__compiled = True
        self.__cmd_list = cmd
        self.__files: list[Path] = files
        self.__folder: Path | None = folder
        return self
    
    def get_command(self) -> tuple[list[str], Path | None]:
        cmd: list[str] | str = self.__cmd_list
        if isinstance(cmd, str):
            cmd += " " + " ".join([str(file.resolve()) for file in self.__files])
        else:
            cmd += [str(file.resolve()) for file in self.__files]
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
    def __init__(self, args_list: list[Path], settings: Settings):
        self.settings = settings
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

        if first.suffix == ".mk":
            self.__prepare_make()
        elif first.suffix == ".ts":
            self.__prepare_ts(free_run_mode)
        elif first.suffix[1:] in self.settings.languages.get_languages().keys():
            self.prepare_exec_with_lang()
        else:
            self.__exec.set_executable([str(x) for x in self.args_list], [], None)

    def replace_placeholders(self, text: str) -> str:
        parent_folder = self.args_list[0].parent
        main_file_without_ext = self.args_list[0].stem
        exe_ext = ".exe" if os.name == "nt" else ""
        output_path = self.cache_dir / ("a.out" + exe_ext)
        
        files_str = " ".join([str(x.relative_to(parent_folder)) for x in self.args_list])
        text = (text.replace("{files}", files_str)
                    .replace("{output}", str(output_path))
                    .replace("{main}", main_file_without_ext)
                    .replace("{cache}", str(self.cache_dir.relative_to(parent_folder))))
        return text

    def prepare_exec_with_lang(self):
        lang = self.settings.languages.get_languages().get(self.args_list[0].suffix[1:], None)
        if lang is None:
            self.__exec.set_compile_error(Text.format("{r}: Extensão de arquivo '" + self.args_list[0].suffix + "' não reconhecida e sem configuração de linguagem", "Falha"))
            return
        build_cmd = lang.build_cmd
        run_cmd = lang.run_cmd
        parent_folder = self.args_list[0].parent
        build_cmd = self.replace_placeholders(build_cmd)
        return_code, stdout, stderr = Runner.subprocess_run(build_cmd, folder=parent_folder, shell_mode=True)
        if return_code != 0:
            self.__exec.set_compile_error(stdout + stderr)
            return
        run_cmd = self.replace_placeholders(run_cmd)
        self.__exec.set_executable(run_cmd.split(), [], parent_folder)

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

    def __prepare_ts(self, free_run_mode: bool):
        
        new_files = self.args_list
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
