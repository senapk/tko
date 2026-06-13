import tempfile
from collections.abc import Callable

import os
import shutil
from tko.util.rt import RT
from tko.util.runner import Runner
from tko.config.settings import Settings
from pathlib import Path
from tko.run_build.ts_macro_preprocessor import TypeScriptMacroPreprocessor
from tko.i18n import Msg


_SOLVER_COMMAND_NOT_FOUND = Msg(
    pt="fail: comando '{name}' não foi encontrado",
    en="fail: command '{name}' was not found",
)
_SOLVER_EXTENSION_UNRECOGNIZED = Msg(
    pt="Falha: Extensão de arquivo '{suffix}' não reconhecida e sem configuração de linguagem",
    en="Fail: File extension '{suffix}' not recognized and no language configuration found",
)
_SOLVER_TS_CONFIG_NOT_FOUND = Msg(
    pt="Falha: Configuração da linguagem 'ts' não encontrada",
    en="Fail: Language configuration for 'ts' not found",
)

class CompileError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message

class Executable:
    def __init__(self, cmd: list[str] | None, files: list[Path] | None, folder: Path):
        if cmd is None:
            cmd = []
        if files is None:
            files = []
        self.__cmd_list: list[str] = cmd
        self.__folder: Path = folder
        self.__compiled: bool = False
        self.__compile_error: bool = False
        self.__error_msg: RT = RT()
    
    
    def set_executable(self, cmd: list[str], files: list[Path], folder: Path):
        self.__compiled = True
        self.__cmd_list = cmd
        self.__files: list[Path] = files
        self.__folder: Path = folder.resolve()
        return self
    
    def get_command(self) -> tuple[list[str] | str, Path]:
        cmd: list[str] = self.__cmd_list
        cmd += [file.resolve().as_posix() for file in self.__files]
        return cmd, self.__folder

    def set_compile_error(self, error_msg: RT | str):
        self.__compiled = True
        self.__compile_error = True
        if isinstance(error_msg, str):
            self.__error_msg = RT(error_msg)
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
    TS_DEFAULT_BUILD_CMD = ["npx", "esbuild", "{files}", "--outdir={cache}", "--format=cjs", "--log-level=error"]
    TS_DEFAULT_RUN_CMD = ["node", "{entry}"]

    def __init__(self, args_list: list[Path], settings: Settings):
        self.settings = settings
        self.args_list: list[Path] = args_list
        self.cache_dir: Path = Path()
        if len(self.args_list) > 0:
            self.cache_dir = self.args_list[0].parent / ".build"
        else:
            self.cache_dir = Path(tempfile.mkdtemp())
        self.clear_cache()
        self.__exec: Executable = Executable(cmd=None, files=None, folder=Path(""))

    def check_tool(self, name: str):
        if shutil.which(name) is None:
            self.__exec.set_compile_error(RT(str(_SOLVER_COMMAND_NOT_FOUND).format(name=name), "r"))
            raise CompileError(str(_SOLVER_COMMAND_NOT_FOUND).format(name=name))

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
            return Executable(cmd=None, files=None, folder=Path("")), False
        if self.__exec.has_compile_error():
            return self.__exec, False
        if not self.__exec.compiled() or force_rebuild:
            self.prepare_exec()
        return self.__exec, True

    def reset(self):
        self.__exec = Executable(cmd=None, files=None, folder=Path(""))
        self.clear_cache()

    def prepare_exec(self) -> None:
        self.reset()
        first = self.args_list[0]

        handlers: dict[str, Callable[[], None]] = {
            ".mk": self.__prepare_make,
            ".ts": self.__prepare_ts,
        }
        handler = handlers.get(first.suffix)

        if handler is not None:
            handler()
        elif first.suffix[1:] in self.settings.get_languages_settings().get_languages().keys():
            self.prepare_exec_with_lang()
        else:
            self.__exec.set_executable([x.as_posix() for x in self.args_list], [], Path(""))

    def replace_placeholders(self, text: list[str]) -> list[str]:
        parent_folder = self.args_list[0].parent
        main_file_without_ext = self.args_list[0].stem
        exe_ext = ".exe" if os.name == "nt" else ""
        output_path = self.cache_dir / ("a.out" + exe_ext)
        entry_path = self.cache_dir / (main_file_without_ext + ".js")
        
        files_flist = [f'{x.relative_to(parent_folder, walk_up=True).as_posix()}' for x in self.args_list]
        output: list[str] = []
        for t in text:
            if t == "{files}":
                output.extend(files_flist)
            else:
                data = (t.replace("{output}", f'{output_path.resolve().as_posix()}')
                            .replace("{main}", main_file_without_ext)
                            .replace("{cache}", f'{self.cache_dir.resolve().as_posix()}')
                            .replace("{entry}", f'{entry_path.resolve().as_posix()}')).strip()
                output.append(data)
        return output

    def prepare_exec_with_lang(self):
        lang = self.settings.get_languages_settings().get_languages().get(self.args_list[0].suffix[1:], None)
        if lang is None:
            self.__exec.set_compile_error(RT(str(_SOLVER_EXTENSION_UNRECOGNIZED).format(suffix=self.args_list[0].suffix), "r"))
            return
        self._prepare_exec_with_commands(lang.build_cmd, lang.run_cmd)

    def _prepare_exec_with_commands(self, build_cmd: list[str], run_cmd: list[str]):
        parent_folder = self.args_list[0].parent
        build_cmd = self.replace_placeholders(build_cmd)
        if len(build_cmd) > 0:
            return_code, stdout, stderr = Runner.subprocess_run(build_cmd, folder=parent_folder)
            if return_code != 0:
                self.__exec.set_compile_error(stdout + stderr)
                return
        run_cmd = self.replace_placeholders(run_cmd)
        self.__exec.set_executable(run_cmd, [], parent_folder)

    def __prepare_make(self):
        self.check_tool("make")
        solver = os.path.abspath(self.args_list[0])
        folder = os.path.dirname(solver)
        cmd = ["make", "-s", "-C", folder, "-f", solver, "build"]
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        if return_code != 0:
            self.__exec.set_compile_error(stdout + stderr)
        else:
            self.__exec.set_executable(cmd=["make", "-s", "-C", folder, "-f", solver, "run"], files=[], folder=Path(""))

    def __prepare_ts(self):
        copy_dir = self.cache_dir / "src"
        if copy_dir.exists():
            shutil.rmtree(copy_dir, ignore_errors=True)
        new_files = TypeScriptMacroPreprocessor.copy_and_patch(self.args_list, copy_dir)

        transpiler = "npx"
        if os.name == "nt":
            transpiler += ".cmd"

        self.check_tool(transpiler)
        self.check_tool("node")

        original_args = self.args_list
        self.args_list = new_files
        try:
            lang = self.settings.get_languages_settings().get_languages().get("ts", None)
            if lang is None:
                self.__exec.set_compile_error(RT(str(_SOLVER_TS_CONFIG_NOT_FOUND), "r"))
                return
            build_cmd = lang.build_cmd
            run_cmd = lang.run_cmd
            if len(build_cmd) == 0:
                build_cmd = self.TS_DEFAULT_BUILD_CMD
            if len(run_cmd) == 0:
                run_cmd = self.TS_DEFAULT_RUN_CMD
            self._prepare_exec_with_commands(build_cmd, run_cmd)
        finally:
            self.args_list = original_args
