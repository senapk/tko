#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import re
import configparser
from typing import List, Optional
import urllib.request
import json
import tempfile
from typing import Any
import subprocess
from typing import Tuple
from subprocess import PIPE
import shutil
from typing import Optional
from enum import Enum
from typing import List, Optional, Tuple
import io
from typing import Tuple, Optional
import urllib.error
from typing import List
from shutil import which
from typing import List, Tuple, Optional
import math
import argparse
import sys



class Title:
    @staticmethod
    def extract_title(readme_file):
        title = open(readme_file).read().split("\n")[0]
        parts = title.split(" ")
        if parts[0].count("#") == len(parts[0]):
            del parts[0]
        title = " ".join(parts)
        return title

class RemoteCfg:
    def __init__(self, url: Optional[str] = None):
        self.user = ""
        self.repo = ""
        self.branch = ""
        self.folder = ""
        self.file = ""
        if url is not None:
            self.from_url(url)

    def from_url(self, url: str):
        if url.startswith("https://raw.githubusercontent.com/"):
            url = url.replace("https://raw.githubusercontent.com/", "")
            parts = url.split("/")
            self.user = parts[0]
            self.repo = parts[1]
            self.branch = parts[2]
            self.folder = "/".join(parts[3:-1])
            self.file = parts[-1]
        elif url.startswith("https://github.com/"):
            url = url.replace("https://github.com/", "")
            parts = url.split("/")
            self.user = parts[0]
            self.repo = parts[1]
            self.branch = parts[3]
            self.folder = "/".join(parts[4:-1])
            self.file = parts[-1]
        else:
            raise Exception("Invalid URL")

    def get_raw_url(self):
        return "https://raw.githubusercontent.com/" + self.user + "/" + self.repo + "/" + self.branch + "/" + self.folder + "/" + self.file

    def download_absolute(self, filename: str):
        try:
            [tempfile, __content] = urllib.request.urlretrieve(self.get_raw_url(), filename)
            content = ""
            try:
                content = open(tempfile, encoding="utf-8").read()
            except:
                content = open(tempfile).read()
            with open(filename, "w", encoding="utf-8") as f:
                absolute = Absolute.relative_to_absolute(content, self)
                f.write(absolute.encode("utf-8").decode("utf-8"))
        except urllib.error.HTTPError:
            print("Error downloading file", self.get_raw_url())
            return

    def __str__(self):
        return f"user: ({self.user}), repo: ({self.repo}), branch: ({self.branch}), folder: ({self.folder}), file: ({self.file})"

    def read(self, cfg_path: str):
        if not os.path.isfile(cfg_path):
            print("no remote.cfg found")

        config = configparser.ConfigParser()
        config.read(cfg_path)

        self.user   = config["DEFAULT"]["user"]
        self.repo   = config["DEFAULT"]["rep"]
        self.branch = config["DEFAULT"]["branch"]
        self.folder = config["DEFAULT"]["base"]
        self.tag    = config["DEFAULT"]["tag"]

    @staticmethod
    def search_cfg_path(source_dir) -> Optional[str]:
        # look for the remote.cfg file in the current folder
        # if not found, look for it in the parent folder
        # if not found, look for it in the parent's parent folder ...

        path = os.path.abspath(source_dir)
        while path != "/":
            cfg_path = os.path.join(path, "remote.cfg")
            if os.path.isfile(cfg_path):
                return cfg_path
            path = os.path.dirname(path)
        return None

class Absolute:

    # processa o conteúdo trocando os links locais para links absolutos utilizando a url remota
    @staticmethod
    def __replace_remote(content: str, remote_raw: str, remote_view: str, remote_folder: str) -> str:
        if content is None or content == "":
            return ""
        if not remote_raw.endswith("/"):
            remote_raw += "/"
        if not remote_view.endswith("/"):
            remote_view += "/"
        if not remote_folder.endswith("/"):
            remote_folder += "/"

        #trocando todas as imagens com link local
        regex = r"!\[(.*?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
        subst = r"![\1](" + remote_raw + r"\3)"
        result = re.sub(regex, subst, content, 0)


        regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?/)\)"
        subst = r"[\1](" + remote_folder + r"\3)"
        result = re.sub(regex, subst, result, 0)

        #trocando todos os links locais cujo conteudo nao seja vazio
        regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
        subst = r"[\1](" + remote_view + r"\3)"
        result = re.sub(regex, subst, result, 0)

        return result

    @staticmethod
    def relative_to_absolute(content: str, cfg: RemoteCfg):
        user_repo = cfg.user + "/" + cfg.repo
        raw = "https://raw.githubusercontent.com"
        github = "https://github.com"
        remote_raw    = f"{raw}/{user_repo}/{cfg.branch}/{cfg.folder}"
        remote_view    = f"{github}/{user_repo}/blob/{cfg.branch}/{cfg.folder}"
        remote_folder = f"{github}/{user_repo}/tree/{cfg.branch}/{cfg.folder}"
        return Absolute.__replace_remote(content, remote_raw, remote_view, remote_folder)

    @staticmethod
    def from_file(source_file, output_file, cfg: RemoteCfg, hook):
        content = open(source_file, encoding="utf-8").read()
        content = Absolute.relative_to_absolute(content, cfg)
        open(output_file, "w").write(content)
        
class RemoteMd:

    # @staticmethod
    # def insert_preamble(lines: List[str], online: str, tkodown: str) -> List[str]:

    #     text = "\n- Veja a versão online: [aqui.](" + online + ")\n"
    #     text += "- Para programar na sua máquina (local/virtual) use:\n"
    #     text += "  - `" + tkodown + "`\n"
    #     text += "- Se não tem o `tko`, instale pelo [LINK](https://github.com/senapk/tko#tko).\n\n---"

    #     lines.insert(1, text)

    #     return lines

    # @staticmethod
    # def insert_qxcode_preamble(cfg: RemoteCfg, content: str, hook) -> str:
    #     base_hook = os.path.join(cfg.base, hook)

    #     lines = content.split("\n")
    #     online_readme_link = os.path.join("https://github.com", cfg.user, cfg.repo, "blob", cfg.branch, base_hook, "Readme.md")
    #     tkodown = "tko down " + cfg.tag + " " + hook
    #     lines = RemoteMd.insert_preamble(lines, online_readme_link, tkodown)
    #     return "\n".join(lines)

    @staticmethod
    def run(remote_cfg: RemoteCfg, source: str, target: str, hook) -> bool:    
        content = open(source).read()
        content = Absolute.relative_to_absolute(content, remote_cfg)
        open(target, "w").write(content)
        return True


class RepoSettings:
    def __init__(self, file: str = ""):
        self.lang: str = ""
        self.url: str = ""
        self.file: str = ""
        self.expanded: list[str] = []
        self.new_items: list[str] = []
        self.tasks: dict[str, str] = {} #notas das tarefas
        self.view: list[str] = []  # lista de flags ligados
        if file != "":
            self.file = os.path.abspath(file)

    def get_file(self) -> str:
        # arquivo existe e é local
        if self.file != "" and os.path.exists(self.file) and self.url == "":
            return self.file
        
        # arquivo não existe e é remoto
        if self.url != "" and (self.file == "" or not os.path.exists(self.file)):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                filename = f.name
                cfg = RemoteCfg(self.url)
                cfg.download_absolute(filename)
            return filename

        # arquivo é local com url remota
        if self.file != "" and os.path.exists(self.file) and self.url != "":
            content = open(self.file, encoding="utf-8").read()
            content = Absolute.relative_to_absolute(content, RemoteCfg(self.url))
            with tempfile.NamedTemporaryFile(delete=False) as f:
                filename = f.name
                f.write(content.encode("utf-8"))
            return filename

        raise ValueError("fail: file not found or invalid settings to download repository file")
        
    def set_file(self, file: str):
        self.file = os.path.abspath(file)
        return self
    
    def set_lang(self, lang: str):
        self.lang = lang
        return self

    def set_url(self, url: str):
        self.url = url
        return self

    def to_dict(self):
        return {
            "lang": self.lang,
            "expanded": self.expanded,
            "new_items": self.new_items,
            "url": self.url,
            "file": self.file,
            "quests": self.expanded,
            "tasks": self.tasks,
            "view": self.view
        }
    
    def from_dict(self, data: dict[str, Any]):
        self.lang = data.get("lang", "")
        self.url = data.get("url", "")
        self.file = data.get("file", "")
        # self.expanded = data.get("expanded", [])
        #verify if expanded is a dict, being get list of values
        try:
            self.expanded = list(data.get("quests", {}).values())
        except AttributeError:
            self.expanded = data.get("expanded", [])
        self.new_items = data.get("new_items", [])
        self.tasks = data.get("tasks", {})
        self.view = data.get("view", [])
        return self

    def __str__(self) -> str:
        return (
            f"url: {self.url}\n"
            f"file: {self.file}\n"
            f"Active: {self.expanded}\n"
            f"Tasks: {self.tasks}\n"
            f"View: {self.view}\n"
        )


class LocalSettings:
    def __init__(self):
        self.rootdir: str = ""
        self.lang: str = ""
        self.ascii: bool = False
        self.color: bool = True
        self.updown: bool = True
        self.sideto_min: int = 60

    def set_rootdir(self, rootdir: str):
        self.rootdir = os.path.abspath(rootdir)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "rootdir": self.rootdir,
            "lang": self.lang,
            "ascii": self.ascii,
            "color": self.color,
            "updown": self.updown,
            "sideto_min": self.sideto_min
        }
    
    def from_dict(self, data: dict[str, Any]):
        self.rootdir = data.get("rootdir", "")
        self.lang = data.get("lang", "")
        self.ascii = data.get("ascii", False)
        self.color = data.get("color", True)
        self.updown = data.get("updown", True)
        self.sideto_min = data.get("sideto_min", 60)
        return self

    def __str__(self) -> str:
        lang = "always ask" if self.lang == "" else self.lang
        return (
            f"Root Directory: {self.rootdir}\n"
            f"Default Language: {lang}\n"
            f"Encoding Mode: {'ASCII' if self.ascii else 'UNICODE'}\n"
            f"Color Mode: {'COLORED' if self.color else 'MONOCHROMATIC'}\n"
            f"Diff Mode: {'SIDE_BY_SIDE' if self.updown else 'UP_DOWN'}\n"
            f"Side-to-Side Min: {self.sideto_min}\n"
        )


class Settings:
    def __init__(self):
        self.reps: dict[str, RepoSettings] = {}
        self.local = LocalSettings()
        self.reps["fup"] = RepoSettings().set_url("https://github.com/qxcodefup/arcade/blob/master/Readme.md")
        self.reps["ed"] = RepoSettings().set_url("https://github.com/qxcodeed/arcade/blob/master/Readme.md")
        self.reps["poo"] = RepoSettings().set_url("https://github.com/qxcodepoo/arcade/blob/master/Readme.md")

    def get_repo(self, course: str) -> RepoSettings:
        if course not in self.reps:
            raise ValueError(f"Course {course} not found in settings")
        return self.reps[course]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "reps": {k: v.to_dict() for k, v in self.reps.items()},
            "local": self.local.to_dict()
        }

    def from_dict(self, data: dict[str, Any]):
        self.reps = {k: RepoSettings().from_dict(v) for k, v in data.get("reps", {}).items()}
        self.local = LocalSettings().from_dict(data.get("local", {}))
        return self
    
    def save_to_json(self, file: str):
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    def __str__(self):
        output = ["Repositories:"]
        maxlen = max([len(key) for key in self.reps])
        for key in self.reps:
            prefix = f"- {key.ljust(maxlen)}"
            if self.reps[key].file and self.reps[key].url:
                output.append(f"{prefix} : dual   : {self.reps[key].url} ; {self.reps[key].file}")
            elif self.reps[key].url:
                output.append(f"{prefix} : remote : {self.reps[key].url}")
            else:
                output.append(f"{prefix} : local  : {self.reps[key].file}")
        return "\n".join(output)


class SettingsParser:

    user_settings_file: str | None = None

    def __init__(self):
        self.package_name = "tko"
        default_filename = "settings.json"
        if SettingsParser.user_settings_file is None:
            self.settings_file = os.path.abspath(default_filename)  # backup for replit, dont remove
        else:
            self.settings_file = os.path.abspath(SettingsParser.user_settings_file)
        self.settings = self.load_settings()

    def get_settings_file(self):
        return self.settings_file

    def load_settings(self) -> Settings:
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                self.settings = Settings().from_dict(json.load(f))
                return self.settings
        except (FileNotFoundError, json.decoder.JSONDecodeError) as _e:
            return self.create_new_settings_file()

    def save_settings(self):
        self.settings.save_to_json(self.settings_file)

    def create_new_settings_file(self) -> Settings:
        self.settings = Settings()
        if not os.path.isdir(self.get_settings_dir()):
            os.makedirs(self.get_settings_dir(), exist_ok=True)
        self.save_settings()
        return self.settings

    def get_settings_dir(self) -> str:
        return os.path.dirname(self.settings_file)
    
    def get_language(self) -> str:
        return self.settings.local.lang



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
    def free_run(cmd: str) -> None:
        answer = subprocess.run(cmd, shell=True, text=True)
        if answer.returncode != 0 and answer.returncode != 1:
            print(Runner.decode_code(answer.returncode))

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




class Color:
    enabled = False
    __terminal_styles = {
        '.': '\033[0m', # Reset
        '*': '\033[1m', # Bold
        '/': '\033[3m', # Italic
        '_': '\033[4m', # Underline
        
        'k': '\033[30m', # Black
        'r': '\033[31m', # Red
        'g': '\033[32m', # Green
        'y': '\033[33m', # Yellow
        'b': '\033[34m', # Blue
        'm': '\033[35m', # Magenta
        'c': '\033[36m', # Cyan
        'w': '\033[37m', # White

        'K': '\033[90m', # Bright black
        'R': '\033[91m', # Bright red
        'G': '\033[92m', # Bright green
        'Y': '\033[93m', # Bright yellow
        'B': '\033[94m', # Bright blue
        'M': '\033[95m', # Bright magenta
        'C': '\033[96m', # Bright cyan
        'W': '\033[97m',

        '#k': '\033[40m', # Background black
        '#r': '\033[41m', # Background red
        '#g': '\033[42m', # Background green
        '#y': '\033[43m', # Background yellow
        '#b': '\033[44m', # Background blue
        '#m': '\033[45m', # Background magenta
        '#c': '\033[46m', # Background cyan
        '#w': '\033[47m', # Background white

        '#K': '\033[100m', # Background bright black
        '#R': '\033[101m', # Background bright red
        '#G': '\033[102m', # Background bright green
        '#Y': '\033[103m', # Background bright yellow
        '#B': '\033[104m', # Background bright blue
        '#M': '\033[105m', # Background bright magenta
        '#C': '\033[106m', # Background bright cyan
        '#W': '\033[107m'  # Background bright white
    }
    __replacements = {
        'black': 'k',
        'red': 'r',
        'green': 'g',
        'yellow': 'y',
        'blue': 'b',
        'magenta': 'm',
        'cyan': 'c',
        'white': 'w',
        'bright_black': 'K',
        'bright_red': 'R',
        'bright_green': 'G',
        'bright_yellow': 'Y',
        'bright_blue': 'B',
        'bright_magenta': 'M',
        'bright_cyan': 'C',
        'bright_white': 'W', 
        'reset': '.',
        'bold': '*',
        'italic': '/',
        'underline': '_',
    }

    @staticmethod
    def get_style(modifier: str):
        if modifier in Color.__replacements:
            modifier = Color.__replacements[modifier]
        if modifier in Color.__terminal_styles:
            return Color.__terminal_styles[modifier]
        print(f'Unknown modifier: {modifier}')
        return ''

    @staticmethod
    def ljust(text: str, width: int) -> str:
        return text + " " * (width - Color.len(text))

    @staticmethod
    def center(text: str, width: int, filler: str) -> str:
        before = filler * ((width - Color.len(text)) // 2)
        after = filler * ((width - Color.len(text) + 1) // 2)
        return before + text + after

    @staticmethod
    def remove_colors(text: str) -> str:
        for color in Color.__terminal_styles.values():
            text = text.replace(color, "")
        return text

    @staticmethod
    def len(text):
        return len(Color.remove_colors(text))


def colour(modifiers: str, text: str) -> str:
    mod = modifiers.split(',')
    output = ''
    for m in [v for v in mod if v != '']:
        val = Color.get_style(m.strip())
        if val != '':
            output += val
    output += text + Color.get_style('reset')
    return output

class __Symbols:
    def __init__(self):
        self.opening = ""
        self.neutral = ""
        self.success = ""
        self.failure = ""
        self.wrong = ""
        self.compilation = ""
        self.execution = ""
        self.unequal = ""
        self.equalbar = ""
        self.hbar = ""
        self.vbar = ""
        self.whitespace = ""  # interpunct
        self.newline = ""  # carriage return
        self.cfill = ""
        self.tab = ""
        self.arrow_up = ""
        self.check = ""  
        self.uncheck = ""
        self.opcheck = ""
        self.opuncheck = ""

        self.ascii = False
        self.set_unicode()

    def get_mode(self) -> str:
        return "ASCII" if self.ascii else "UTF-8"

    def set_ascii(self):
        self.ascii = True

        self.opening = "=> "
        self.neutral = "."
        self.success = "S"
        self.failure = "X"
        self.wrong = "W"
        self.compilation = "C"
        self.execution = "E"
        self.unequal = "#"
        self.equalbar = "|"
        self.hbar = "─"
        self.vbar = "│"
        self.whitespace = "\u2E31"  # interpunct
        self.newline = "\u21B5"  # carriage return
        self.cfill = "_"
        self.tab = "    "
        self.arrow_up = "A"

        self.check = "x"  
        self.uncheck = " "
        self.opcheck = "█"
        self.opuncheck = "▒"

    def set_unicode(self):
        self.ascii = False

        self.opening = "=> "
        self.neutral = "»"
        self.success = "✓"
        self.failure = "✗"
        self.wrong = "ω"
        self.compilation = "ϲ"
        self.execution = "ϵ"
        self.unequal = "├"
        self.equalbar = "│"
        self.hbar = "─"
        self.vbar = "│"
        self.whitespace = "\u2E31"  # interpunct
        self.newline = "\u21B5"  # carriage return
        self.cfill = "_"
        self.tab = "    "
        self.arrow_up = "↑"

        self.check = "✓"  
        self.uncheck = "✗"
        self.opcheck = "ⴲ"
        self.opuncheck = "ⵔ"


    def set_colors(self):
        self.opening = colour("b", self.opening)
        self.neutral = colour("b", self.neutral)
        self.success = colour("g", self.success)
        self.failure = colour("r", self.failure)
        self.wrong = colour("r", self.wrong)
        self.compilation = colour("y", self.compilation)
        self.execution = colour("y", self.execution)
        self.unequal = colour("r", self.unequal)
        self.equalbar = colour("g", self.equalbar)


symbols = __Symbols()

def green(text: str):
    return colour("g", text)

def red(text: str):
    return colour("r", text)

def yellow(text: str):
    return colour("y", text)

def magenta(text: str):
    return colour("m", text)

def cyan(text: str):
    return colour("c", text)


class Report:
    __term_width: Optional[int] = None

    def __init__(self):
        pass

    @staticmethod
    def update_terminal_size():
        term_width = shutil.get_terminal_size().columns
        if term_width % 2 == 0:
            term_width -= 1
        Report.__term_width = term_width

    @staticmethod
    def get_terminal_size():
        if Report.__term_width is None:
            Report.update_terminal_size()

        return Report.__term_width

    @staticmethod
    def set_terminal_size(value: int):
        if value % 2 == 0:
            value -= 1
        Report.__term_width = value

    @staticmethod
    def centralize(
        text,
        sep=" ",
        left_border: Optional[str] = None,
        right_border: Optional[str] = None,
    ) -> str:
        if left_border is None:
            left_border = sep
        if right_border is None:
            right_border = sep
        term_width = Report.get_terminal_size()

        size = Color.len(text)
        pad = sep if size % 2 == 0 else ""
        tw = term_width - 2
        filler = sep * int(tw / 2 - size / 2)
        return left_border + pad + filler + text + filler + right_border




class ExecutionResult(Enum):
    UNTESTED = "untested_"
    SUCCESS = "correct__"
    WRONG_OUTPUT = "wrong_out"
    COMPILATION_ERROR = "compilati"
    EXECUTION_ERROR = "execution"

    @staticmethod
    def get_symbol(result) -> str:
        if result == ExecutionResult.UNTESTED:
            return symbols.neutral
        elif result == ExecutionResult.SUCCESS:
            return symbols.success
        elif result == ExecutionResult.WRONG_OUTPUT:
            return symbols.wrong
        elif result == ExecutionResult.COMPILATION_ERROR:
            return symbols.compilation
        elif result == ExecutionResult.EXECUTION_ERROR:
            return symbols.execution
        else:
            raise ValueError("Invalid result type")

    def __str__(self):
        return self.value


class CompilerError(Exception):
    pass


class DiffMode(Enum):
    FIRST = "MODE: SHOW FIRST FAILURE ONLY"
    ALL = "MODE: SHOW ALL FAILURES"
    QUIET = "MODE: SHOW NONE FAILURES"


class IdentifierType(Enum):
    OBI = "OBI"
    MD = "MD"
    TIO = "TIO"
    VPL = "VPL"
    SOLVER = "SOLVER"


class Identifier:
    def __init__(self):
        pass

    @staticmethod
    def get_type(target: str) -> IdentifierType:
        if os.path.isdir(target):
            return IdentifierType.OBI
        elif target.endswith(".md"):
            return IdentifierType.MD
        elif target.endswith(".tio"):
            return IdentifierType.TIO
        elif target.endswith(".vpl"):
            return IdentifierType.VPL
        else:
            return IdentifierType.SOLVER


class Unit:
    def __init__(self, case: str = "", inp: str = "", outp: str = "", grade: Optional[int] = None, source: str = ""):
        self.source = source  # stores the source file of the unit
        self.source_pad = 0  # stores the pad to justify the source file
        self.case = case  # name
        self.case_pad = 0  # stores the pad to justify the case name
        self.input = inp  # input
        self.output = outp  # expected output
        self.user: Optional[str] = None  # solver generated answer
        self.grade: Optional[int] = grade  # None represents proportional gr, 100 represents all
        self.grade_reduction: int = 0  # if grade is None, this atribute should be filled with the right grade reduction
        self.index = 0
        self.repeated: Optional[int] = None

        self.result: ExecutionResult = ExecutionResult.UNTESTED

    def __str__(self):
        index = str(self.index).zfill(2)
        grade = str(self.grade_reduction).zfill(3)
        rep = "" if self.repeated is None else "[" + str(self.repeated) + "]"
        op = ExecutionResult.get_symbol(self.result) + " " + self.result.value
        pad = self.source.ljust(self.source_pad)
        return f"({op})[{index}] GR:{grade} {pad} ({rep})"


class Param:

    def __init__(self):
        pass

    class Basic:
        def __init__(self):
            self.index: Optional[int] = None
            self.label_pattern: Optional[str] = None
            self.is_up_down: bool = False
            self.diff_mode = DiffMode.FIRST
            self.filter: bool = False
            self.compact: bool = False

        def set_index(self, value: Optional[int]):
            self.index: Optional[int] = value
            return self

        def set_label_pattern(self, label_pattern: Optional[str]):
            self.label_pattern: Optional[str] = label_pattern
            return self
        
        def set_compact(self, value: bool):
            self.compact = value
            return self

        def set_up_down(self, value: bool):
            self.is_up_down = value
            return self
    
        def set_filter(self, value: bool):
            self.filter = value
            return self

        def set_diff_mode(self, value: DiffMode):
            self.diff_mode = value
            return self

    class Manip:
        def __init__(self):
            self.unlabel: bool = False
            self.to_sort: bool = False
            self.to_number: bool = False
        
        def set_unlabel(self, value: bool):
            self.unlabel = value
            return self
        
        def set_to_sort(self, value: bool):
            self.to_sort = value
            return self
        
        def set_to_number(self, value: bool):
            self.to_number = value
            return self




class Diff:

    @staticmethod
    def make_line_arrow_up(a: str, b: str) -> str:
        hdiff = ""
        first = True
        i = 0
        lim = max(len(a), len(b))
        while i < lim:
            if i >= len(a) or i >= len(b) or a[i] != b[i]:
                if first:
                    first = False
                    hdiff += symbols.arrow_up
            else:
                hdiff += " "
            i += 1
        return hdiff

    @staticmethod
    def render_white(text: Optional[str], color: Optional[str] = None) -> Optional[str]:
        if text is None:
            return None
        if color is None:
            text = text.replace(' ', symbols.whitespace)
            text = text.replace('\n', symbols.newline + '\n')
            return text
        text = text.replace(' ', colour(color, symbols.whitespace))
        text = text.replace('\n', colour("r", symbols.newline) + '\n')
        return text

    # create a string with both ta and tb side by side with a vertical bar in the middle
    @staticmethod
    def side_by_side(ta: List[str], tb: List[str], unequal: str = symbols.unequal):
        cut = (Report.get_terminal_size() - 6) // 2
        upper = max(len(ta), len(tb))
        data = []

        for i in range(upper):
            a = ta[i] if i < len(ta) else "###############"
            b = tb[i] if i < len(tb) else "###############"
            if len(a) < cut:
                a = a.ljust(cut)
            # if len(a) > cut:
            #     a = a[:cut]
            if i >= len(ta) or i >= len(tb) or ta[i] != tb[i]:
                data.append(unequal + " " + a + " " + unequal + " " + b)
            else:
                data.append(symbols.vbar + " " + a + " " + symbols.vbar + " " + b)

        return "\n".join(data)

    # a_text -> clean full received
    # b_text -> clean full expected
    # first_failure -> index of the first line unmatched 
    @staticmethod
    def first_failure_diff(a_text: str, b_text: str, first_failure) -> str:
        def get(vet, index):
            if index < len(vet):
                return vet[index]
            return ""

        a_render = Diff.render_white(a_text).splitlines()
        b_render = Diff.render_white(b_text).splitlines()

        first_a = get(a_render, first_failure)
        first_b = get(b_render, first_failure)
        greater = max(Color.len(first_a), Color.len(first_b))

        if first_failure > 0:
            lbefore = Color.remove_colors(get(a_render, first_failure - 1))
            greater = max(greater, Color.len(lbefore))

        out_a, out_b = Diff.colorize_2_lines_diff(first_a, first_b)

        postext = symbols.vbar + " " + Color.ljust(out_a, greater) + colour("g", " (expected)") + "\n"
        postext += symbols.vbar + " " + Color.ljust(out_b, greater) + colour("r", " (received)") + "\n"
        postext += (symbols.vbar + " " + Color.ljust(Diff.make_line_arrow_up(first_a, first_b), greater)
                    + colour("b", " (mismatch)") + "\n")
        return postext

    @staticmethod
    def find_first_mismatch(line_a: str, line_b: str) -> int: 
        i = 0
        while i < len(line_a) and i < len(line_b):
            if line_a[i] != line_b[i]:
                return i
            i += 1
        return i
    
    @staticmethod
    def colorize_2_lines_diff(la: str, lb: str, neut: str = "w", exp: str = "g", rec: str = "r") -> Tuple[str, str]:
        pos = Diff.find_first_mismatch(la, lb)
        a_out = colour(neut, la[0:pos]) + colour(exp, la[pos:])
        b_out = colour(neut, lb[0:pos]) + colour(rec, lb[pos:])
        return a_out, b_out

    # return a tuple of two strings with the diff and the index of the  first mismatch line
    @staticmethod
    def render_diff(a_text: str, b_text: str, pad: Optional[bool] = None) -> Tuple[List[str], List[str], int]:
        a_lines = a_text.splitlines()
        b_lines = b_text.splitlines()

        a_output = []
        b_output = []

        a_size = len(a_lines)
        b_size = len(b_lines)
        
        first_failure = -1

        cut: int = 0
        if pad is True:
            cut = (Report.get_terminal_size() - 6) // 2

        max_size = max(a_size, b_size)

        # lambda function to return element in index i or empty if out of bounds
        def get(vet, index):
            out = ""
            if index < len(vet):
                out = vet[index]
            if pad is None:
                return out
            return out[:cut].ljust(cut)

        # get = lambda vet, i: vet[i] if i < len(vet) else ""

        for i in range(max_size):
            a_data = get(a_lines, i)
            b_data = get(b_lines, i)
            
            if i >= a_size or i >= b_size or a_lines[i] != b_lines[i]:
                if first_failure == -1:
                    first_failure = i
                a_out, b_out = Diff.colorize_2_lines_diff(a_data, b_data, "yellow")
                a_output.append(a_out)
                b_output.append(b_out)
            else:
                a_output.append(a_data)
                b_output.append(b_data)

        return a_output, b_output, first_failure

    @staticmethod
    def mount_up_down_diff(unit: Unit) -> str:
        output = io.StringIO()

        string_input = unit.input
        string_expected = unit.output
        string_received = unit.user

        # dotted = "-"

        expected_lines, received_lines, first_failure = Diff.render_diff(string_expected, string_received)
        string_input = "\n".join([symbols.vbar + " " + line for line in string_input.split("\n")])[0:-2]
        unequal = symbols.unequal
        if unit.result == ExecutionResult.EXECUTION_ERROR:
            unequal = symbols.vbar
        expected_lines, received_lines = Diff.put_left_equal(expected_lines, received_lines, unequal)

        output.write(Report.centralize("", symbols.hbar, "╭") + "\n")
        output.write(Report.centralize(str(unit), " ", symbols.vbar) + "\n")
        output.write(Report.centralize(colour("b", " INPUT "), symbols.hbar, "├") + "\n")
        output.write(string_input)
        output.write(Report.centralize(colour("g", " EXPECTED "), symbols.hbar, "├") + "\n")
        output.write("\n".join(expected_lines) + "\n")
        output.write(Report.centralize(colour("r", " RECEIVED "), symbols.hbar, "├") + "\n")
        output.write("\n".join(received_lines) + "\n")
        if unit.result != ExecutionResult.EXECUTION_ERROR:
            output.write(Report.centralize(colour("bold", " WHITESPACE "),  symbols.hbar, "├") + "\n")
            output.write(Diff.first_failure_diff(string_expected, string_received, first_failure))
        output.write(Report.centralize("",  symbols.hbar, "╰") + "\n")

        return output.getvalue()

    @staticmethod
    def put_left_equal(exp_lines: List[str], rec_lines: List[str], unequal: str = symbols.unequal):

        max_size = max(len(exp_lines), len(rec_lines))

        for i in range(max_size):
            if i >= len(exp_lines) or i >= len(rec_lines) or (exp_lines[i] != rec_lines[i]):
                exp_lines[i] = unequal + " " + exp_lines[i]
                rec_lines[i] = unequal + " " + rec_lines[i]
            else:
                exp_lines[i] = symbols.vbar + " " + exp_lines[i]
                rec_lines[i] = symbols.vbar + " " + rec_lines[i]
        
        return exp_lines, rec_lines
            
    @staticmethod
    def mount_side_by_side_diff(unit: Unit) -> str:

        def title_side_by_side(left, right, filler=" ", middle=" ", prefix=""):
            half = int((Report.get_terminal_size() - len(middle)) / 2)
            line = ""
            a = Color.center(left, half, filler)
            if Color.len(a) > half:
                a = a[:half]
            line += a
            line += middle
            b = Color.center(right, half, filler)
            if Color.len(b) > half:
                b = b[:half]
            line += b
            if prefix != "":
                line = prefix + line[1:]
            return line

        output = io.StringIO()

        string_input = unit.input
        string_expected = unit.output
        string_received = unit.user

        # dotted = "-"
        # vertical_separator = symbols.vbar
        hbar = symbols.hbar

        expected_lines, received_lines, first_failure = Diff.render_diff(string_expected, string_received, True)
        output.write(Report.centralize("", hbar, "╭") + "\n")
        output.write(Report.centralize(str(unit), " ", "│") + "\n")
        input_header = colour("b", " INPUT ")
        output.write(title_side_by_side(input_header, input_header, hbar, "┬", "├") + "\n")
        if string_input != "":
            output.write(Diff.side_by_side(string_input.split("\n")[:-1], string_input.split("\n")[:-1]) + "\n")
        expected_header = colour("g", " EXPECTED ")
        received_header = colour("r", " RECEIVED ")
        output.write(title_side_by_side(expected_header, received_header, hbar, "┼", "├") + "\n")
        unequal = symbols.unequal
        if unit.result == ExecutionResult.EXECUTION_ERROR:
            unequal = symbols.vbar
        output.write(Diff.side_by_side(expected_lines, received_lines, unequal) + "\n")
        if unit.result != ExecutionResult.EXECUTION_ERROR:
            output.write(Report.centralize(colour("bold", " WHITESPACE "),  symbols.hbar, "├") + "\n")
            output.write(Diff.first_failure_diff(string_expected, string_received, first_failure))
        output.write(Report.centralize("",  symbols.hbar, "╰") + "\n")

        return output.getvalue()




class Down:

    ts_draft = (r'let _cin_ : string[] = [];' + '\n'
                r'try { _cin_ = require("fs").readFileSync(0).toString().split(/\r?\n/); } catch(e){}' + '\n'
                r'let input = () : string => _cin_.length === 0 ? "" : _cin_.shift()!;' + '\n'
                r'let write = (text: any, end:string="\n")=> process.stdout.write("" + text + end);' + '\n')

    js_draft = (r'let __lines = require("fs").readFileSync(0).toString().split("\n");' + '\n'
                r'let input = () => __lines.length === 0 ? "" : __lines.shift();' + '\n'
                r'let write = (text, end="\n") => process.stdout.write("" + text + end);') + '\n'
    
    c_draft = '#include <stdio.h>\n\nint main() {\n    return 0;\n}\n\n'
    cpp_draft = '#include <iostream>\n\nint main() {\n}\n\n'

    drafts = {'c': c_draft, 'cpp': cpp_draft, 'ts': ts_draft, 'js': js_draft}
    # def __init__(self):
    #     self.drafts = {}
    #     self.drafts['c'] = Down.c_draft
    #     self.drafts['cpp'] = Down.cpp_draft
    #     self.drafts['ts'] = Down.ts_draft
    #     self.drafts['js'] = Down.js_draft

    # @staticmethod
    # def update():
    #     if os.path.isfile(".info"):
    #         data = open(".info", "r").read().split("\n")[0]
    #         data = data.split(" ")
    #         discp = data[0]
    #         label = data[1]
    #         ext = data[2]
    #         Down.entry_unpack(".", discp, label, ext)
    #     else:
    #         print("No .info file found, skipping update...")

    @staticmethod
    def __create_file(content, path, label=""):
        with open(path, "w") as f:
            f.write(content)
        print("  " + path, label)

    @staticmethod
    def __unpack_json(loaded, destiny, lang: str):
        # extracting all files to folder
        for entry in loaded["upload"]:
            if entry["name"] == "vpl_evaluate.cases":
                Down.__compare_and_save(entry["contents"], os.path.join(destiny, "cases.tio"))

        # for entry in loaded["keep"]:
        #    Down.compare_and_save(entry["contents"], os.path.join(destiny, entry["name"]))

        # for entry in loaded["required"]:
        #    path = os.path.join(destiny, entry["name"])
        #    Down.compare_and_save(entry["contents"], path)

        if "draft" in loaded:
            if lang in loaded["draft"]:
                for file in loaded["draft"][lang]:
                    path = os.path.join(destiny, file["name"])
                    Down.__create_file(file["contents"], path, "(Draft)")

    @staticmethod
    def __compare_and_save(content, path):
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.encode("utf-8").decode("utf-8"))
            print("  " + path + " (New)")
        else:
            if open(path).read() != content:
                print(path + " (Updated)")
                with open(path, "w") as f:
                    f.write(content)
            else:
                print("  " + path + " (Unchanged)")
    
    @staticmethod
    def __down_problem_def(destiny, cache_url) -> Tuple[str, str]:
        # downloading Readme
        readme = os.path.join(destiny, "Readme.md")
        [tempfile, __content] = urllib.request.urlretrieve(cache_url + "Readme.md")

        # content = ""
        try:
            content = open(tempfile, encoding="utf-8").read()
        except FileNotFoundError:
            content = open(tempfile).read()

        Down.__compare_and_save(content, readme)
        
        # downloading mapi
        mapi = os.path.join(destiny, "mapi.json")
        urllib.request.urlretrieve(cache_url + "mapi.json", mapi)
        return readme, mapi

    @staticmethod
    def __create_problem_folder(rootdir: str, activity: str) -> str:
        # create dir
        destiny: str = os.path.join(rootdir, activity)
        if not os.path.exists(destiny):
            os.makedirs(destiny, exist_ok=True)
        else:
            print("  Problem folder", destiny, "found, merging content.")

        return destiny

    @staticmethod
    def download_problem(rootdir, course: str, activity: str, language: Optional[str]) -> bool:
        sp = SettingsParser()
        settings = sp.load_settings()
        rep = settings.get_repo(course)

        file = rep.get_file()
        game = Game(file)
        item = game.get_task(activity)
        if not item.link.startswith("http"):
            print("fail: link for activity is not a remote link")
            return False
        cfg = RemoteCfg(item.link)
        cache_url = os.path.dirname(cfg.get_raw_url()) + "/.cache/"

        destiny = Down.__create_problem_folder(rootdir, activity)
        try:
            # print("debug", cache_url)
            [_readme_path, mapi_path] = Down.__down_problem_def(destiny, cache_url)
        except urllib.error.HTTPError:
            print("  fail: activity not found in course url")
            # verifi if destiny folder is empty and remove it
            if len(os.listdir(destiny)) == 0:
                os.rmdir(destiny)
            return False

        with open(mapi_path) as f:
            loaded_json = json.load(f)
        os.remove(mapi_path)

        language_def = SettingsParser().get_language()
        ask_ext = False
        if language is None:
            if language_def != "":
                language = language_def
            else:
                print("  Choose extension for draft: [c, cpp, py, ts, js, java]: ", end="")
                language = input()
                ask_ext = True
        
        Down.__unpack_json(loaded_json, destiny, language)
        Down.__download_drafts(loaded_json, destiny, language, cache_url, ask_ext)
        return True

    @staticmethod
    def __download_drafts(loaded_json, destiny: str, language, cache_url, ask_ext):
        if len(loaded_json["required"]) == 1:  # you already have the students file
            return

        if "draft" in loaded_json and language in loaded_json["draft"]:
            pass
        else:
            try:
                draft_path = os.path.join(destiny, "draft." + language)
                urllib.request.urlretrieve(cache_url + "draft." + language, draft_path)
                print("  " + draft_path + " (Draft) Rename before modify.")

            except urllib.error.HTTPError:  # draft not found
                filename = "draft."
                draft_path = os.path.join(destiny, filename + language)
                if not os.path.exists(draft_path):
                    with open(draft_path, "w") as f:
                        if language in Down.drafts:
                            f.write(Down.drafts[language])
                        else:
                            f.write("")
                    print("  " + draft_path, "(Empty)")
        
        if ask_ext:
            print("\nYou can choose default extension with command\n$ tko config -l <extension>")





def check_tool(name):
    if which(name) is None:
        raise CompilerError("fail: " + name + " executable not found")


class Solver:
    def __init__(self, solver_list: List[str]):
        self.path_list: List[str] = [Solver.__add_dot_bar(path) for path in solver_list]
        
        self.temp_dir = tempfile.mkdtemp()
        self.error_msg: str = ""
        self.executable: str = ""
        if len(self.path_list) > 0:
            self.prepare_exec()

    def prepare_exec(self) -> None:
        path = self.path_list[0]

        if path.endswith(".py"):
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
        elif path.endswith(".sql"):
            self.__prepare_sql()
        else:
            self.executable = path

    def __prepare_java(self):
        check_tool("javac")

        solver = self.path_list[0]

        filename = os.path.basename(solver)
        # tempdir = os.path.dirname(self.path_list[0])

        cmd = ["javac"] + self.path_list + ['-d', self.temp_dir]
        cmd = " ".join(cmd)
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        print(stdout)
        print(stderr)
        if return_code != 0:
            raise CompilerError(stdout + stderr)
        self.executable = "java -cp " + self.temp_dir + " " + filename[:-5]  # removing the .java

    def __prepare_js(self):
        check_tool("node")
        solver = self.path_list[0]
        self.executable = "node " + solver

    def __prepare_sql(self):
        check_tool("sqlite3")
        self.executable = "cat " + " ".join(self.path_list) + " | sqlite3"

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
        print(stdout + stderr)
        if return_code != 0:
            raise CompilerError(stdout + stderr)
        jsfile = os.path.join(self.temp_dir, filename[:-3] + ".js")
        self.executable = "node " + jsfile  # renaming solver to main
    
    def __prepare_c_cpp(self, pre_args: List[str], pos_args: List[str]):
        # solver = self.path_list[0]
        tempdir = self.temp_dir
        source_list = self.path_list
        # print("Using the following source files: " + str([os.path.basename(x) for x in source_list]))
        
        exec_path = os.path.join(tempdir, ".a.out")
        cmd = pre_args + source_list + ["-o", exec_path] + pos_args
        return_code, stdout, stderr = Runner.subprocess_run(" ".join(cmd))
        if return_code != 0:
            raise CompilerError(stdout + stderr)
        self.executable = exec_path

    def __prepare_c(self):
        check_tool("gcc")
        pre = ["gcc", "-Wall"]
        pos = ["-lm", "-lutil"]
        self.__prepare_c_cpp(pre, pos)

    def __prepare_cpp(self):
        check_tool("g++")
        pre = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror"]
        pos = []
        self.__prepare_c_cpp(pre, pos)

    @staticmethod
    def __add_dot_bar(solver: str) -> str:
        if os.sep not in solver and os.path.isfile("." + os.sep + solver):
            solver = "." + os.sep + solver
        return solver
    


class FileSource:
    def __init__(self, label, input_file, output_file):
        self.label = label
        self.input_file = input_file
        self.output_file = output_file

    def __eq__(self, other):
        return self.label == other.label and self.input_file == other.input_file and \
                self.output_file == other.output_file


class PatternLoader:
    pattern: str = ""

    def __init__(self):
        parts = PatternLoader.pattern.split(" ")
        self.input_pattern = parts[0]
        self.output_pattern = parts[1] if len(parts) > 1 else ""
        self._check_pattern()

    def _check_pattern(self):
        self.__check_double_wildcard()
        self.__check_missing_wildcard()

    def __check_double_wildcard(self):
        if self.input_pattern.count("@") > 1 or self.output_pattern.count("@") > 1:
            raise ValueError("  fail: the wildcard @ should be used only once per pattern")

    def __check_missing_wildcard(self):
        if "@" in self.input_pattern and "@" not in self.output_pattern:
            raise ValueError("  fail: is input_pattern has the wildcard @, the input_patter should have too")
        if "@" not in self.input_pattern and "@" in self.output_pattern:
            raise ValueError("  fail: is output_pattern has the wildcard @, the input_pattern should have too")

    def make_file_source(self, label):
        return FileSource(label, self.input_pattern.replace("@", label), self.output_pattern.replace("@", label))

    def get_file_sources(self, filename_list: List[str]) -> List[FileSource]:
        input_re = self.input_pattern.replace(".", "\\.")
        input_re = input_re.replace("@", "(.*)")
        file_source_list = []
        for filename in filename_list:
            match = re.findall(input_re, filename)
            if not match:
                continue
            label = match[0]
            file_source = self.make_file_source(label)
            if file_source.output_file not in filename_list:
                print("fail: file " + file_source.output_file + " not found")
            else:
                file_source_list.append(file_source)
        return file_source_list

    def get_odd_files(self, filename_list) -> List[str]:
        matched = []
        sources = self.get_file_sources(filename_list)
        for source in sources:
            matched.append(source.input_file)
            matched.append(source.output_file)
        unmatched = [file for file in filename_list if file not in matched]
        return unmatched




class VplParser:
    @staticmethod
    def finish(text):
        return text if text.endswith("\n") else text + "\n"

    @staticmethod
    def unwrap(text):
        while text.endswith("\n"):
            text = text[:-1]
        if text.startswith("\"") and text.endswith("\""):
            text = text[1:-1]
        return VplParser.finish(text)

    @staticmethod
    class CaseData:
        def __init__(self, case="", inp="", outp="", grade: Optional[int] = None):
            self.case: str = case
            self.input: str = VplParser.finish(inp)
            self.output: str = VplParser.unwrap(VplParser.finish(outp))
            self.grade: Optional[int] = grade

        def __str__(self):
            return "case=" + self.case + '\n' \
                   + "input=" + self.input \
                   + "output=" + self.output \
                   + "gr=" + str(self.grade)

    regex_vpl_basic = r"case= *([ \S]*) *\n *input *=(.*?)^ *output *=(.*)"
    regex_vpl_extended = r"case= *([ \S]*) *\n *input *=(.*?)^ *output *=(.*?)^ *grade *reduction *= *(\S*)% *\n?"

    @staticmethod
    def filter_quotes(x):
        return x[1:-2] if x.startswith('"') else x

    @staticmethod
    def split_cases(text: str) -> List[str]:
        regex = r"^ *[Cc]ase *="
        subst = "case="
        text = re.sub(regex, subst, text, 0, re.MULTILINE | re.DOTALL)
        return ["case=" + t for t in text.split("case=")][1:]

    @staticmethod
    def extract_extended(text) -> Optional[CaseData]:
        f = re.match(VplParser.regex_vpl_extended, text, re.MULTILINE | re.DOTALL)
        if f is None:
            return None
        try:
            gr = int(f.group(4))
        except ValueError:
            gr = None
        return VplParser.CaseData(f.group(1), f.group(2), f.group(3), gr)

    @staticmethod
    def extract_basic(text) -> Optional[CaseData]:
        m = re.match(VplParser.regex_vpl_basic, text, re.MULTILINE | re.DOTALL)
        if m is None:
            return None
        return VplParser.CaseData(m.group(1), m.group(2), m.group(3), None)

    @staticmethod
    def parse_vpl(content: str) -> List[CaseData]:
        text_cases = VplParser.split_cases(content)
        seq: List[VplParser.CaseData] = []

        for text in text_cases:
            case = VplParser.extract_extended(text)
            if case is not None:
                seq.append(case)
                continue
            case = VplParser.extract_basic(text)
            if case is not None:
                seq.append(case)
                continue
            print("invalid case: " + text)
            exit(1)
        return seq

    @staticmethod
    def to_vpl(unit: CaseData):
        text = "case=" + unit.case + "\n"
        text += "input=" + unit.input
        text += "output=\"" + unit.output + "\"\n"
        if unit.grade is not None:
            text += "grade reduction=" + str(unit.grade) + "%\n"
        return text


class Loader:
    regex_tio = r"^ *>>>>>>>> *(.*?)\n(.*?)^ *======== *\n(.*?)^ *<<<<<<<< *\n?"

    def __init__(self):
        pass

    @staticmethod
    def parse_cio(text, source):
        unit_list = []
        text = "\n" + text

        pattern = r'```.*?\n(.*?)```'  # get only inside code blocks
        code = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        # join all code blocks found
        text = "\n" + "\n".join(code)

        pieces = []  # header, input, output

        open_case = False
        for line in text.split("\n"):
            if line.startswith("#__case") or line.startswith("#TEST_CASE"):
                pieces.append({"header": line, "input": [], "output": []})
                open_case = True
            elif open_case:
                pieces[-1]["output"].append(line)
                if line.startswith("$end"):
                    open_case = False

        # concatenando testes contínuos e finalizando testes sem $end
        for i in range(len(pieces)):
            output = pieces[i]["output"]
            if output[-1] != "$end" and i < len(pieces) - 1:
                pieces[i + 1]["output"] = output + pieces[i + 1]["output"]
                output.append("$end")

        # removendo linhas vazias e criando input das linhas com $
        for piece in pieces:
            piece["input"] = [line[1:] for line in piece["output"] if line.startswith("$")]
            piece["output"] = [line for line in piece["output"] if line != "" and not line.startswith("#")]

        for piece in pieces:
            case = " ".join(piece["header"].split(" ")[1:])
            inp = "\n".join(piece["input"]) + "\n"
            output = "\n".join(piece["output"]) + "\n"
            unit_list.append(Unit(case, inp, output, None, source))

        for unit in unit_list:
            unit.fromCio = True

        return unit_list

    @staticmethod
    def parse_tio(text: str, source: str = "") -> List[Unit]:

        # identifica se tem grade e retorna case name e grade
        def parse_case_grade(value: str) -> Tuple[str, Optional[int]]:
            if value.endswith("%"):
                words = value.split(" ")
                last = value.split(" ")[-1]
                _case = " ".join(words[:-1])
                grade_str = last[:-1]           # ultima palavra sem %
                try:
                    _grade = int(grade_str)
                    return _case, _grade
                except ValueError:
                    pass
            return value, None

        matches = re.findall(Loader.regex_tio, text, re.MULTILINE | re.DOTALL)
        unit_list = []
        for m in matches:
            case, grade = parse_case_grade(m[0])
            unit_list.append(Unit(case, m[1], m[2], grade, source))
        return unit_list

    @staticmethod
    def parse_vpl(text: str, source: str = "") -> List[Unit]:
        data_list = VplParser.parse_vpl(text)
        output: List[Unit] = []
        for m in data_list:
            output.append(Unit(m.case, m.input, m.output, m.grade, source))
        return output

    @staticmethod
    def parse_dir(folder) -> List[Unit]:
        pattern_loader = PatternLoader()
        files = sorted(os.listdir(folder))
        matches = pattern_loader.get_file_sources(files)

        unit_list: List[Unit] = []
        try:
            for m in matches:
                unit = Unit()
                unit.source = os.path.join(folder, m.label)
                unit.grade = 100
                with open(os.path.join(folder, m.input_file)) as f:
                    value = f.read()
                    unit.input = value + ("" if value.endswith("\n") else "\n")
                with open(os.path.join(folder, m.output_file)) as f:
                    value = f.read()
                    unit.output = value + ("" if value.endswith("\n") else "\n")
                unit_list.append(unit)
        except FileNotFoundError as e:
            print(str(e))
        return unit_list

    @staticmethod
    def parse_source(source: str) -> List[Unit]:
        if os.path.isdir(source):
            return Loader.parse_dir(source)
        if os.path.isfile(source):
            #  if PreScript.exists():
            #      source = PreScript.process_source(source)
            with open(source) as f:
                content = f.read()
            if source.endswith(".vpl"):
                return Loader.parse_vpl(content, source)
            elif source.endswith(".tio"):
                return Loader.parse_tio(content, source)
            elif source.endswith(".md"):
                tests = Loader.parse_tio(content, source)
                tests += Loader.parse_cio(content, source)
                return tests
            else:
                print("warning: target format do not supported: " + source)  # make this a raise
        else:
            raise FileNotFoundError('warning: unable to find: ' + source)
        return []




class Writer:

    def __init__(self):
        pass

    @staticmethod
    def to_vpl(unit: Unit):
        text = "case=" + unit.case + "\n"
        text += "input=" + unit.input
        text += "output=\"" + unit.output + "\"\n"
        if unit.grade is None:
            text += "\n"
        else:
            text += "grade reduction=" + str(unit.grade).zfill(3) + "%\n"
        return text

    @staticmethod
    def to_tio(unit: Unit):
        text = ">>>>>>>>"
        if unit.case != '':
            text += " " + unit.case
        if unit.grade is not None:
            text += " " + str(unit.grade) + "%"
        text += '\n' + unit.input
        text += "========\n"
        text += unit.output
        if unit.output != '' and unit.output[-1] != '\n':
            text += '\n'
        text += "<<<<<<<<\n"
        return text

    @staticmethod
    def save_dir_files(folder: str, pattern_loader: PatternLoader, label: str, unit: Unit) -> None:
        file_source = pattern_loader.make_file_source(label)
        with open(os.path.join(folder, file_source.input_file), "w") as f:
            f.write(unit.input)
        with open(os.path.join(folder, file_source.output_file), "w") as f:
            f.write(unit.output)

    @staticmethod
    def save_target(target: str, unit_list: List[Unit], force: bool = False):
        def ask_overwrite(file):
            print("file " + file + " found. Overwrite? (y/n):")
            resp = input()
            if resp.lower() == 'y':
                print("overwrite allowed")
                return True
            print("overwrite denied\n")
            return False

        def save_dir(_target: str, _unit_list):
            folder = _target
            pattern_loader = PatternLoader()
            number = 0
            for unit in _unit_list:
                Writer.save_dir_files(folder, pattern_loader, str(number).zfill(2), unit)
                number += 1

        def save_file(_target, _unit_list):
            if _target.endswith(".tio"):
                _new = "\n".join([Writer.to_tio(unit) for unit in _unit_list])
            else:
                _new = "\n".join([Writer.to_vpl(unit) for unit in _unit_list])

            file_exists = os.path.isfile(_target)

            if file_exists:
                _old = open(_target).read()
                if _old == _new:
                    print("no changes in test file")
                    return

            if not file_exists or (file_exists and (force or ask_overwrite(_target))):
                with open(_target, "w") as f:
                    f.write(_new)

                    if not force:
                        print("file " + _target + " wrote")

        target_type = Identifier.get_type(target)
        if target_type == IdentifierType.OBI:
            save_dir(target, unit_list)
        elif target_type == IdentifierType.TIO or target_type == IdentifierType.VPL:
            save_file(target, unit_list)
        else:
            print("fail: target " + target + " do not supported for build operation\n")



# generate label for cases


class LabelFactory:
    def __init__(self):
        self._label = ""
        self._index = -1

    def index(self, value: int):
        try:
            self._index = int(value)
        except ValueError:
            raise ValueError("Index on label must be a integer")
        return self

    def label(self, value: str):
        self._label = value
        return self

    def generate(self):
        label = LabelFactory.trim_spaces(self._label)
        label = LabelFactory.remove_old_index(label)
        if self._index != -1:
            index = str(self._index).zfill(2)
            if label != "":
                return index + " " + label
            else:
                return index
        return label

    @staticmethod
    def trim_spaces(text):
        parts = text.split(" ")
        parts = [word for word in parts if word != '']
        return " ".join(parts)

    @staticmethod
    def remove_old_index(label):
        split_label = label.split(" ")
        if len(split_label) > 0:
            try:
                int(split_label[0])
                return " ".join(split_label[1:])
            except ValueError:
                return label


class Wdir:
    def __init__(self):
        self.solver: Optional[Solver] = None
        self.source_list: List[str] = []
        self.pack_list: List[List[Unit]] = []
        self.unit_list: List[Unit] = []

    def set_solver(self, solver_list: List[str]):
        if len(solver_list) > 0:
            self.solver = Solver(solver_list)
        return self

    def set_sources(self, source_list: List[str]):
        self.source_list = source_list
        return self

    def set_target_list(self, target_list: List[str]):
        target_list = [t for t in target_list if t != ""]
        for target in target_list:
            if not os.path.exists(target):
                raise FileNotFoundError(colour("red", "fail: ") + target + " not found")

        solvers = [target for target in target_list if Identifier.get_type(target) == IdentifierType.SOLVER]
        sources = [target for target in target_list if Identifier.get_type(target) != IdentifierType.SOLVER]
        
        self.set_solver(solvers)
        self.set_sources(sources)
        return self

    def set_cmd(self, exec_cmd: Optional[str]):
        if exec_cmd is None:
            return self
        if self.solver is not None:
            print("fail: if using --cmd, don't pass source files to target")
        self.solver = Solver([])
        self.solver.executable = exec_cmd
        return self

    def build(self):
        loading_failures = 0
        for source in self.source_list:
            try:
                self.pack_list.append(Loader.parse_source(source))
            except FileNotFoundError as e:
                print(str(e))
                loading_failures += 1
                pass
        if loading_failures > 0 and loading_failures == len(self.source_list):
            raise FileNotFoundError("failure: none source found")
        self.unit_list = sum(self.pack_list, [])
        self.__number_and_mark_duplicated()
        self.__calculate_grade()
        self.__pad()
        return self

    def calc_grade(self) -> int:
        grade = 100
        for case in self.unit_list:
            if not case.repeated and (case.user is None or case.output != case.user):
                grade -= case.grade_reduction
        return max(0, grade)

    # put all the labels with the same length
    def __pad(self):
        if len(self.unit_list) == 0:
            return
        max_case = max([len(x.case) for x in self.unit_list])
        max_source = max([len(x.source) for x in self.unit_list])
        for unit in self.unit_list:
            unit.case_pad = max_case
            unit.source_pad = max_source

    # select a single unit to execute exclusively
    def filter(self, param: Param.Basic):
        index = param.index
        if index is not None:
            if 0 <= index < len(self.unit_list):
                self.unit_list = [self.unit_list[index]]
            else:
                raise ValueError("Index Number out of bounds: " + str(index))
        return self

    # calculate the grade reduction for the cases without grade
    # the grade is proportional to the number of unique cases
    def __calculate_grade(self):
        unique_count = len([x for x in self.unit_list if not x.repeated])
        for unit in self.unit_list:
            if unit.grade is None:
                unit.grade_reduction = math.floor(100 / unique_count)
            else:
                unit.grade_reduction = unit.grade

    # number the cases and mark the repeated
    def __number_and_mark_duplicated(self):
        new_list = []
        index = 0
        for unit in self.unit_list:
            unit.index = index
            index += 1
            search = [x for x in new_list if x.input == unit.input]
            if len(search) > 0:
                unit.repeated = search[0].index
            new_list.append(unit)
        self.unit_list = new_list

    # sort, unlabel ou rename using the param received
    def manipulate(self, param: Param.Manip):
        # filtering marked repeated
        self.unit_list = [unit for unit in self.unit_list if unit.repeated is None]
        if param.to_sort:
            self.unit_list.sort(key=lambda v: len(v.input))
        if param.unlabel:
            for unit in self.unit_list:
                unit.case = ""
        if param.to_number:
            number = 00
            for unit in self.unit_list:
                unit.case = LabelFactory().label(unit.case).index(number).generate()
                number += 1

    def unit_list_resume(self):
        return "\n".join([str(unit) for unit in self.unit_list])

    def resume(self) -> str:

        def sources() -> str:
            out = []
            if len(self.pack_list) == 0:
                out.append(symbols.failure)
            for i in range(len(self.pack_list)):
                nome: str = self.source_list[i].split(os.sep)[-1]
                out.append(nome + "(" + str(len(self.pack_list[i])).zfill(2) + ")")
            return colour("green", "base:") + "[" + ", ".join(out) + "]"

        def solvers() -> str:
            path_list = [] if self.solver is None else self.solver.path_list

            if self.solver is not None and len(path_list) == 0:  # free_cmd
                out = "free cmd"
            else:
                out = ", ".join([os.path.basename(path) for path in path_list])
            return colour("green", "prog:") + "[" + out + "]"

        # folder = os.getcwd().split(os.sep)[-1]
        # tests_count = (colour("tests:", Color.GREEN) +
        #               str(len([x for x in self.unit_list if x.repeated is None])).zfill(2))

        return symbols.opening + sources() + " " + solvers()




class Execution:

    def __init__(self):
        pass

    # run a unit using a solver and return if the result is correct
    @staticmethod
    def run_unit(solver: Solver, unit: Unit) -> ExecutionResult:
        cmd = solver.executable
        return_code, stdout, stderr = Runner.subprocess_run(cmd, unit.input)
        unit.user = stdout + stderr
        if return_code != 0:
            return ExecutionResult.EXECUTION_ERROR
        if unit.user == unit.output:
            return ExecutionResult.SUCCESS
        return ExecutionResult.WRONG_OUTPUT


class FilterMode:

    @staticmethod
    def deep_copy_and_change_dir():
        # path to ~/.tko_filter
        filter_path = os.path.join(os.path.expanduser("~"), ".tko_filter")

        # verify if filter command is available
        if shutil.which("filter") is None:
            print("ERROR: filter command not found")
            print("Install feno with 'pip install feno'")
            exit(1)

        subprocess.run(["filter", "-rf", ".", "-o", filter_path])

        os.chdir(filter_path)


class Run:

    def __init__(self, target_list: List[str], exec_cmd: Optional[str], param: Param.Basic):
        self.target_list = target_list
        self.exec_cmd = exec_cmd
        self.param = param
        self.wdir = None

    def execute(self):
        self.remove_duplicates()
        self.change_targets_to_filter_mode()
        if not self.build_wdir():
            return
        if self.missing_target():
            return
        if self.list_mode():
            return
        if self.free_run():
            return
        self.diff_mode()
        return

    def remove_duplicates(self):
        # remove duplicates in target list keeping the order
        self.target_list = list(dict.fromkeys(self.target_list))

    def change_targets_to_filter_mode(self):
        if self.param.filter:
            old_dir = os.getcwd()

            print(Report.centralize(" Entering in filter mode ", "═"))
            FilterMode.deep_copy_and_change_dir()  
            # search for target outside . dir and redirect target
            new_target_list = []
            for target in self.target_list:
                if ".." in target:
                    new_target_list.append(os.path.normpath(os.path.join(old_dir, target)))
                elif os.path.exists(target):
                    new_target_list.append(target)
            self.target_list = new_target_list

    def print_top_line(self):
        print(self.wdir.resume(), end="")
        print(" [", end="", flush=True)
        first = True
        for unit in self.wdir.unit_list:
            if first:
                first = False
            else:
                print(" ", end="", flush=True)
            unit.result = Execution.run_unit(self.wdir.solver, unit)
            print(ExecutionResult.get_symbol(unit.result), end="", flush=True)
        print("]")

    def print_diff(self):
        if self.param.diff_mode == DiffMode.QUIET:
            return
        
        results = [unit.result for unit in self.wdir.unit_list]
        if ExecutionResult.EXECUTION_ERROR not in results and ExecutionResult.WRONG_OUTPUT not in results:
            return
        
        if not self.param.compact:
            print(self.wdir.unit_list_resume())
        
        if self.param.diff_mode == DiffMode.FIRST:
            # printing only the first wrong case
            wrong = [unit for unit in self.wdir.unit_list if unit.result != ExecutionResult.SUCCESS][0]
            if self.param.is_up_down:
                print(Diff.mount_up_down_diff(wrong))
            else:
                print(Diff.mount_side_by_side_diff(wrong))
            return

        if self.param.diff_mode == DiffMode.ALL:
            for unit in self.wdir.unit_list:
                if unit.result != ExecutionResult.SUCCESS:
                    if self.param.is_up_down:
                        print(Diff.mount_up_down_diff(unit))
                    else:
                        print(Diff.mount_side_by_side_diff(unit))

    def build_wdir(self) -> bool:
        try:
            self.wdir = Wdir().set_target_list(self.target_list).set_cmd(self.exec_cmd).build().filter(self.param)
        except CompilerError as e:
            print(e)
            return False
        except FileNotFoundError as e:
            print(e)
            return False
        return True

    def missing_target(self) -> bool:
        # no solver and no test cases
        if self.wdir.solver is None and len(self.wdir.unit_list) == 0:
            print(colour("red", "fail: ") + "No solver or tests found.")
            return True
        return False
    
    def list_mode(self) -> bool:
        # list mode
        if self.wdir.solver is None and len(self.wdir.unit_list) > 0:
            print(Report.centralize(" No solvers found. Listing Test Cases ", "╌"), flush=True)
            print(self.wdir.resume())
            print(self.wdir.unit_list_resume())
            return True
        return False

    def free_run(self) -> bool:
        # free run mode
        if self.wdir.solver is not None and len(self.wdir.unit_list) == 0:
            t = Report.centralize(" No test cases found. Running: " + self.wdir.solver.executable + " ", symbols.hbar)
            print(t, flush=True)
            # force print to terminal
            Runner.free_run(self.wdir.solver.executable)
            return True
        return False

    def diff_mode(self):
        print(Report.centralize(" Running solver against test cases ", "═"))
        self.print_top_line()
        self.print_diff()


class Build:

    def __init__(self, target_out: str, source_list: List[str], param: Param.Manip, to_force: bool):
        self.target_out = target_out
        self.source_list = source_list
        self.param = param
        self.to_force = to_force

    def execute(self):
        try:
            wdir = Wdir().set_sources(self.source_list).build()
            wdir.manipulate(self.param)
            Writer.save_target(self.target_out, wdir.unit_list, self.to_force)
        except FileNotFoundError as e:
            print(str(e))
            return False
        return True

tko_guide = """
       ╔════ TKO GUIA COMPACTO ════╗
╔══════╩═════ BAIXAR PROBLEMA ═════╩═══════╗
║        tko down <curso> <label>          ║
║ exemplo poo  : tko down poo carro        ║
║ exemplo fup  : tko down fup opala        ║
╟─────────── EXECUTAR SEM TESTAR ──────────╢
║          tko run <cod, cod...>           ║
║exemplo ts  : tko run solver.ts           ║
║exemplo cpp : tko run main.cpp lib.cpp    ║
╟──────────── RODAR OS TESTES ─────────────╢
║   tko run cases.tio <cod, ...> [-i ind]  ║
║ exemplo: tko run cases.tio main.ts       ║
║só ind 6: tko run cases.tio main.c -i 6   ║
╟── DEFINIR EXTENSÃO PADRÃO DOS RASCUNHOS ─╢
║           tko config -l <ext>            ║
║     exemplo c : tko config -l c          ║
║  exemplo java : tko config -l java       ║
╟─────────── MUDAR VISUALIZAÇÃO ───────────╢
║             tko config <--opcao>         ║
║DiffMode: tko config [--side  | --updown ]║
║Cores   : tko config [--mono  | --color  ]║
║Encoding: tko config [--ascii | --unicode]║
╚══════════════════════════════════════════╝
"""

bash_guide = """
       ╔═══ BASH  GUIA COMPACTO ════╗
╔══════╩════ MOSTRAR E NAVEGAR ═════╩══════╗
║Mostrar arquivos  : ls                    ║
║Mostrar ocultos   : ls -la                ║
║Mudar de pasta    : cd _nome_da_pasta     ║
║Subir um nível    : cd ..                 ║
╟─────────────── CRIAR ────────────────────╢
║Criar um arquivo  : touch _nome_do_arquivo║
║Criar uma pasta   : mkdir _nome_da_pasta  ║
╟─────────────── REMOVER ──────────────────╢
║Apagar um arquivo : rm _nome_do_arquivo   ║
║Apagar uma pasta  : rm -r _nome_da_pasta  ║
║Renomear ou mover : mv _antigo _novo      ║
╟─────────────── CONTROLAR ────────────────╢
║Últimos comandos  : SETA PRA CIMA         ║
║Limpar console    : Control L             ║
║Cancelar execução : Control C             ║
║Finalizar entrada : Control D             ║
╚══════════════════════════════════════════╝
"""
#!/usr/bin/env python3



class Task:
    def __init__(self):
        self.line_number = 0
        self.line = ""
        self.key = ""
        self.grade: int = 0 #valor de 0 a 10
        self.skills = []
        self.title = ""
        self.link = ""
        self.opt = False
        self.default_min_value = 7


    def get_grade_color(self, min_value: int | None = None) -> str:
        if min_value is None:
            min_value = self.default_min_value
        if self.grade == 0:
            return "m"
        if self.grade < min_value:
            return "r"
        if self.grade < 10:
            return "y"
        if self.grade == 10:
            return "g"
        return "w"  

    def get_grade_symbol(self, min_value: int | None = None) -> str:
        if min_value is None:
            min_value = self.default_min_value
        color = self.get_grade_color(min_value)
        if self.grade == 0:
            return colour("*," + color, symbols.uncheck)
        if self.grade < min_value:
            return colour("*," + color, str(self.grade))
        if self.grade < 10:
            return colour("*," + color, str(self.grade))
        if self.grade == 10:
            return colour("*," + color, symbols.check)
        return "0"


    def get_percent(self):
        if self.grade == 0:
            return 0
        if self.grade == 10:
            return 100
        return self.grade * 10
    
    def is_complete(self):
        return self.grade == 10

    def not_started(self):
        return self.grade == 0
    
    def in_progress(self):
        return self.grade > 0 and self.grade < 10

    def set_grade(self, grade: int):
        grade = int(grade)
        if grade >= 0 and grade <= 10:
            self.grade = grade
        else:
            print(f"Grade inválida: {grade}")

    @staticmethod
    def parse_item_with_link(line) -> tuple[bool, str, str]:
        pattern = r"\ *-.*\[(.*?)\]\((.+?)\)"
        match = re.match(pattern, line)
        if match:
            return True, match.group(1), match.group(2)
        return False, "", ""
    
    @staticmethod
    def parse_task_with_link(line) -> tuple[bool, str, str]:
        pattern = r"\ *- \[ \].*\[(.*?)\]\((.+?)\)"
        match = re.match(pattern, line)
        if match:
            return True, match.group(1), match.group(2)
        return False, "", ""

    def load_html_tags(self):                   
        pattern = r"<!--\s*(.*?)\s*-->"
        match = re.search(pattern, self.line)
        if not match:
            return

        tags_raw = match.group(1).strip()
        tags = [tag.strip() for tag in tags_raw.split(" ")]
        self.opt = "opt" in tags
        for t in tags:
            if t.startswith("s:"):
                self.skills.append(t[2:])
            elif t.startswith("@"):
                self.key = t[1:]

        
    @staticmethod
    def parse_arroba_from_title_link(titulo, link) -> tuple[bool, str]:
        pattern = r".*?@(\w*)"
        match = re.match(pattern, titulo)
        if not match:
            return False, ""
        key = match.group(1)
        if not (key + "/Readme.md") in link:
            return False, ""
        return True, key

    def process_link(self, base_file):
        if self.link.startswith("http"):
            return
        if self.link.startswith("./"):
            self.link = self.link[2:]
        # todo trocar / por \\ se windows
        self.link = base_file + self.link

    # - [Titulo com @palavra em algum lugar](link/@palavra/Readme.md) <!-- tag1 tag2 tag3 -->
    def parse_coding_task(self, line, line_num):
        if line == "":
            return False
        line = line.lstrip()

        found, titulo, link = Task.parse_item_with_link(line)
        if not found:
            return False
        found, key = Task.parse_arroba_from_title_link(titulo, link)
        if not found:
            return False

        self.line = line
        self.line_number = line_num
        self.key = key
        self.title = titulo
        self.link = link

        self.load_html_tags()

        return True

    # se com - [ ], não precisa das tags dentro do html, o key será dado pelo título
    # se tiver as tags dentro do html, se alguma começar com @, o key será dado por ela
    # - [ ] [Título](link)
    # - [ ] [Título](link) <!-- tag1 tag2 tag3 -->
    # - [Título](link) <!-- tag1 tag2 tag3 -->
    def parse_reading_task(self, line, line_num):
        if line == "":
            return False
        line = line.lstrip()

        found, titulo, link = Task.parse_task_with_link(line)
        if found:
            self.key = link
            self.title = titulo
            self.link = link
            self.line = line
            self.line_number = line_num
            self.load_html_tags()
            return True
        
        found, titulo, link = Task.parse_item_with_link(line)
        self.key = ""
        if found:
            self.link = link
            self.line = line
            self.line_number = line_num
            self.load_html_tags()
            if self.key == "":
                return False
            self.title = titulo
            return True

        return False

    def __str__(self):
        line = str(self.line_number).rjust(3)
        key = "" if self.key == self.title else self.key + " "
        return f"{line}    {self.grade} {key}{self.title} {self.skills} {self.link}"

class Quest:
    def __init__(self):
        self.line_number = 0
        self.line = ""
        self.key = ""
        self.title = ""
        self.tasks: list[Task] = []
        self.skills: list[str] = [] # s:skill
        self.cluster = ""
        self.requires = [] # r:quest_key
        self.requires_ptr = []
        self.opt = False # opt
        self.qmin: int | None = None # q:  minimo de 50 porcento da pontuação total para completar
        self.tmin: int | None = None  # t: ou ter no mínimo esse valor de todas as tarefas

    def __str__(self):
        line = str(self.line_number).rjust(3)
        tasks_size = str(len(self.tasks)).rjust(2, "0")
        key = "" if self.key == self.title else self.key + " "
        output = f"{line}   {tasks_size} {key}{self.title} {self.skills} {self.requires}"
        return output

    def get_resume_by_percent(self) -> str:
        value = self.get_percent()
        # ref = self.qmin if self.qmin is not None else 100
        # if self.qmin is None:
        #     return colour("*", str(value) + "%")
        return colour(self.get_grade_color() + ",*", str(value)) + "%"
    
    def get_requirement(self):
        if self.qmin is not None:
            return colour("y", f"[{self.qmin}%]")
        if self.tmin is not None:
            return colour("y", f"[t>{self.tmin - 1}]")
        return ""

    def get_resume_by_tasks(self) -> str:
        tmin = self.tmin if self.tmin is not None else 7
        total = len([t for t in self.tasks if not t.opt])
        plus = len([t for t in self.tasks if t.opt])
        count = len([t for t in self.tasks if t.grade >= tmin])
        output = f"{count}/{total}"
        if plus > 0:
            output += f"+{plus}"
        # if self.tmin is None:
        #     return "(" + colour("*", output) + ")"
        return "(" + colour(self.get_grade_color()+",*", output) + ")"

    def get_grade_color(self) -> str:
        if self.not_started():
            return "magenta"
        if not self.is_complete():
            return "red"
        if self.get_percent() == 100:
            return "green"
        return "yellow"

    def is_complete(self):
        if self.qmin is not None:
            return self.is_complete_by_percent()
        if self.tmin is not None:
            return self.is_complete_by_tasks()
        return False

    def is_complete_by_percent(self):
        if self.qmin is None:
            return False
        return self.get_percent() >= self.qmin
    
    def is_complete_by_tasks(self):
        if self.tmin is None:
            return False
        for t in self.tasks:
            if not t.opt and t.grade < self.tmin:
                return False
        return True

    def get_percent(self):
        total = len(self.tasks)
        if total == 0:
            return 0
        done = sum([t.get_percent() for t in self.tasks])
        return done // total

    def in_progress(self):
        if self.is_complete():
            return False
        for t in self.tasks:
            if t.grade != 0:
                return True
        return False

    def not_started(self):
        if self.is_complete():
            return False
        if self.in_progress():
            return False
        return True

    def is_reachable(self, cache: dict[str, bool]):
        if self.key in cache:
            return cache[self.key]

        if len(self.requires_ptr) == 0:
            cache[self.key] = True
            return True
        cache[self.key] = all( [r.is_complete() and r.is_reachable(cache) for r in self.requires_ptr] )
        return cache[self.key]

    def update_requirements(self):
        if self.qmin is None and self.tmin is None:
            self.qmin = 50

    def parse_quest(self, line, line_num):
        
        fullpattern = r"^#+\s*(.*?)<!--\s*(.*?)\s*-->\s*$"
        match = re.match(fullpattern, line)
        tags = []

        self.line = line
        self.line_number = line_num
        self.cluster = ""

        if match:
            self.title = match.group(1).strip()
            tags_raw = match.group(2).strip()
            tags = [tag.strip() for tag in tags_raw.split()]
            keys = [t[1:] for t in tags if t.startswith("@")]
            if len(keys) > 0:
                self.key = keys[0]
            else:
                self.key = get_md_link(self.title)
            self.skills = [t[2:] for t in tags if t.startswith("s:")]
            self.requires = [t[2:] for t in tags if t.startswith("r:")]
            self.opt = "opt" in tags
            qmin = [t[2:] for t in tags if t.startswith("q:")]
            if len(qmin) > 0:
                self.qmin = int(qmin[0])
            tmin = [t[2:] for t in tags if t.startswith("t:")]
            if len(tmin) > 0:
                self.tmin = int(tmin[0])
                if self.tmin > 10:
                    print("fail: tmin > 10")
                    exit(1)
            self.update_requirements()
            return True

        minipattern = r"^#+\s*(.*?)\s*$"
        match = re.match(minipattern, line)
        if match:
            self.title = match.group(1)
            self.key = get_md_link(self.title)
            self.update_requirements()
            return True
        
        return False

class Cluster:
    def __init__(self, line_number:int = 0, title: str = "", key: str = ""):
        self.line_number = line_number
        self.title: str = title
        self.key: str = key
        self.quests: list[Quest] = []

    def __str__(self):
        line = str(self.line_number).rjust(3)
        quests_size = str(len(self.quests)).rjust(2, "0")
        key = "" if self.key == self.title else self.key + " "
        return f"{line} {quests_size} {key}{self.title}"
    
    def get_grade_color(self) -> str:
        perc = self.get_percent()
        if perc == 0:
            return "m"
        if perc < 50:
            return "r"
        if perc < 100:
            return "y"
        return "g"

    def get_percent(self):
        total = 0
        for q in self.quests:
            total += q.get_percent()
        return total // len(self.quests)

    def get_resume_by_percent(self) -> str:
        return colour(self.get_grade_color() + ",*", f"{self.get_percent()}%")

    def get_resume_by_quests(self):
        total = len(self.quests)
        count = len([q for q in self.quests if q.is_complete()])
        return f"({count}/{total})"
        

def rm_comments(title: str) -> str:
    if "<!--" in title and "-->" in title:
        title = title.split("<!--")[0] + title.split("-->")[1]
    return title


def get_md_link(title: str) -> str:
    if title is None:
        return ""
    title = title.lower()
    out = ""
    for c in title:
        if c == " " or c == "-":
            out += "-"
        elif c == "_":
            out += "_"
        elif c.isalnum():
            out += c
    return out


class Game:
    def __init__(self, file: str | None = None):
        self.clusters: list[Cluster] = []  # clusters ordered
        self.quests: dict[str, Quest] = {}  # quests indexed by quest key
        self.tasks: dict[str, Task] = {}  # tasks indexed by task key
        if file is not None:
            self.parse_file(file)

    def get_task(self, key: str) -> Task:
        if key in self.tasks:
            return self.tasks[key]
        raise Exception(f"fail: task {key} not found in course definition")

    # se existir um cluster nessa linha, insere na lista de clusters e retorno o objeto cluster inserido
    def load_cluster(self, line: str, line_num: int) -> Cluster | None:
        pattern = r"^#+\s*(.*?)<!--\s*(.*?)\s*-->\s*$"
        match = re.match(pattern, line)
        if not match:
            return None
        titulo = match.group(1)
        tags_raw = match.group(2).strip()
        tags = [tag.strip() for tag in tags_raw.split(" ")]
        if not "group" in tags:
            return None
        
        keys = [tag[1:] for tag in tags if tag.startswith("@")]
        key = titulo
        if len(keys) > 0:
            key = keys[0]
        
        cluster = Cluster(line_num, titulo, key)

        # search for existing cluster in self.clusters
        for c in self.clusters:
            if c.key == key:
                print(f"Cluster {key} já existe")
                print(c)
                print(cluster)
                exit(1)
                
        self.clusters.append(cluster)
        return cluster
                

    def load_quest(self, line, line_num) -> Quest | None:
        quest = Quest()
        if not quest.parse_quest(line, line_num + 1):
            return None
        if quest.key in self.quests:
            print(f"Quest {quest.key} já existe")
            print(quest)
            print(self.quests[quest.key])
            exit(1)
        self.quests[quest.key] = quest
        return quest

    def load_task(self, line, line_num) -> Task | None:
        if line == "":
            return None
        task = Task()
        found = False
        if task.parse_reading_task(line, line_num + 1):
            found = True
        if task.parse_coding_task(line, line_num + 1):
            found = True
        if not found:
            return None
        
        if task.key in self.tasks:
            print(f"Task {task.key} já existe")
            print(task)
            print(self.tasks[task.key])
            exit(1)
        self.tasks[task.key] = task
        return task

    # Verificar se todas as quests requeridas existem e adiciona o ponteiro
    # Verifica se todas as quests tem tarefas
    def validate_requirements(self):

        # verify is there are keys repeated between quests, tasks and groups

        keys = [c.key for c in self.clusters] +\
               [k for k in self.quests.keys()] +\
               [k for k in self.tasks.keys()]

        # print chaves repetidas
        for k in keys:
            if keys.count(k) > 1:
                print(f"Chave repetida: {k}")
                exit(1)

        # remove all quests without tasks
        valid_quests = {}
        for k, q in self.quests.items():
            if len(q.tasks) > 0:
                valid_quests[k] = q

        self.quests = valid_quests

        # for q in self.quests.values():
        #   if len(q.tasks) == 0:
        #     print(f"Quest {q.key} não tem tarefas")
        #     exit(1)

        for q in self.quests.values():
            for r in q.requires:
                if r in self.quests:
                    q.requires_ptr.append(self.quests[r])
                else:
                    print(f"keys: {self.quests.keys()}")
                    print(f"Quest\n{str(q)}\nrequer {r} que não existe")
                    exit(1)

        # check if there is a cycle

    def check_cycle(self):
        def dfs(qx, visitedx):
            if len(visitedx) > 0:
                if visitedx[0] == qx.key:
                    print(f"Cycle detected: {visitedx}")
                    exit(1)
            if q.key in visitedx:
                return
            visitedx.append(q.key)
            for r in q.requires_ptr:
                dfs(r, visitedx)

        for q in self.quests.values():
            visited: list[str] = []
            dfs(q, visited)

    def parse_file(self, file):
        lines = open(file, encoding="utf-8").read().split("\n")
        active_quest = None
        active_cluster = None

        for line_num, line in enumerate(lines):
            cluster = self.load_cluster(line, line_num)
            if cluster is not None:
                active_cluster = cluster
                continue
            
            quest = self.load_quest(line, line_num)
            if quest is not None:
                active_quest = quest
                if active_cluster is None:
                    self.clusters.append(Cluster(0, "Sem grupo", "Sem grupo"))
                    active_cluster = self.clusters[-1]
                quest.cluster = active_cluster.key
                active_cluster.quests.append(quest)
                continue

            task = self.load_task(line, line_num)
            if task is not None:
                if active_quest is None:
                    print(f"Task {task.key} não está dentro de uma quest")
                    print(task)
                    exit(1)
                active_quest.tasks.append(task)

        self.clear_empty()

        self.validate_requirements()
        for t in self.tasks.values():
            t.process_link(os.path.dirname(file) + "/")

    def clear_empty(self):

        # apagando quests vazias da lista de quests
        for k in list(self.quests.keys()):
            if len(self.quests[k].tasks) == 0:
                del self.quests[k]

        # apagando quests vazias dos clusters e clusters vazios
        clusters = []
        for c in self.clusters:
            quests = [q for q in c.quests if len(q.tasks) > 0]
            if len(quests) > 0:
                c.quests = quests
                clusters.append(c)
        self.clusters = clusters

    def get_reachable_quests(self):
        # cache needs to be reseted before each call
        cache: dict[str, bool] = {}
        return [q for q in self.quests.values() if q.is_reachable(cache)]

    def __str__(self):
        output = []
        for c in self.clusters:
            output.append(str(c))
            for q in c.quests:
                output.append(str(q))
                for t in q.tasks:
                    output.append(str(t))
        return "\n".join(output)


class Graph:

    colorlist: list[tuple[str, str]] = [
            ("aquamarine3","aquamarine4"),
            ("bisque3","bisque4"),
            ("brown3","brown4"),
            ("chartreuse3","chartreuse4"),
            ("coral3","coral4"),
            ("cyan3","cyan4"),
            ("darkgoldenrod3","darkgoldenrod4"),
            ("darkolivegreen3","darkolivegreen4"),
            ("darkorchid3","darkorchid4"),
            ("darkseagreen3","darkseagreen4"),
            ("darkslategray3","darkslategray4"),
            ("deeppink3","deeppink4"),
            ("deepskyblue3","deepskyblue4"),
            ("dodgerblue3","dodgerblue4"),
            ("firebrick3","firebrick4"),
            ("gold3","gold4"),
            ("green3","green4"),
            ("hotpink3","hotpink4"),
            ("indianred3","indianred4"),
            ("khaki3","khaki4"),
            ("lightblue3","lightblue4"),
            ("lightcoral","lightcoral"),
            ("lightcyan3","lightcyan4"),
            ("lightgoldenrod3","lightgoldenrod4"),
            ("lightgreen","lightgreen"),
            ("lightpink3","lightpink4"),
            ("lightsalmon3","lightsalmon4"),
            ("lightseagreen","lightseagreen"),
            ("lightskyblue3","lightskyblue4"),
            ("lightsteelblue3","lightsteelblue4"),
            ("lightyellow3","lightyellow4"),
            ("magenta3","magenta4"),
            ("maroon3","maroon4"),
            ("mediumorchid3","mediumorchid4"),
            ("mediumpurple3","mediumpurple4"),
            ("mediumspringgreen","mediumspringgreen"),
            ("mediumturquoise","mediumturquoise"),
            ("mediumvioletred","mediumvioletred"),
            ("mistyrose3","mistyrose4"),
            ("navajowhite3","navajowhite4"),
            ("olivedrab3","olivedrab4"),
            ("orange3","orange4"),
            ("orangered3","orangered4"),
            ("orchid3","orchid4"),
            ("palegreen3","palegreen4"),
            ("paleturquoise3","paleturquoise4"),
            ("palevioletred3","palevioletred4")
            ]

    def __init__(self, game: Game):
        self.game = game
        self.reachable: list[str] | None = None
        self.counts: dict[str, str] | None = None
        self.graph_ext = ".png"
        self.output = "graph"

    def set_reachable(self, reachable: list[str]):
        self.reachable = reachable
        return self

    def set_counts(self, counts: dict[str, str]):
        self.counts = counts
        return self

    def set_graph_ext(self, graph_ext: str):
        self.graph_ext = graph_ext
        return self
    
    def set_output(self, output: str):
        self.output = output
        return self

    def info(self, qx: Quest):
        text = f'{qx.title.strip()}'
        if self.reachable is None:
            return f'"{text}"'
        return f'"{text}\\n{self.counts[qx.key]}"'


    def is_reachable_or_next(self, q: Quest):
        if self.reachable is None:
            return True
        if q.key in self.reachable:
            return True
        for r in q.requires_ptr:
            if r.key in self.reachable:
                return True
        return False

    def generate(self):
        saida = ["digraph diag {", '  node [penwidth=1, style="rounded,filled", shape=box]']

        targets = [q for q in self.game.quests.values() if self.is_reachable_or_next(q)]
        for q in targets:
            token = "->"
            if len(q.requires_ptr) > 0:
                for r in q.requires_ptr:
                    extra = ""
                    if self.reachable is not None:
                        if q.key not in self.reachable and not r.is_complete():
                            extra = "[style=dotted]"
                    saida.append(f"  {self.info(r)} {token} {self.info(q)} {extra}")
            else:
                v = '  "Início"'
                saida.append(f"{v} {token} {self.info(q)}")

        for i, c in enumerate(self.game.clusters):
            cluster_targets = [q for q in c.quests if self.is_reachable_or_next(q)]
            for q in cluster_targets:
                if q.opt:
                    fillcolor = self.colorlist[i][0]
                    textcolor = "white"
                else:
                    fillcolor = self.colorlist[i][0]
                    textcolor = "black"
                shape = "ellipse"
                color = "black"
                width = 1
                if self.reachable is not None:
                    if q.key not in self.reachable:
                        color = "white"
                    else:
                        width = 3
                        color = q.get_grade_color()
                saida.append(f"  {self.info(q)} [shape={shape}, color={color}, penwidth={width}, fillcolor={fillcolor}, style=filled, fontcolor={textcolor}]")


        # for c in self.clusters:
        #     key = get_md_link(c.key).replace("-", "_")
        #     saida.append(f"  subgraph cluster_{key}{{")
        #     saida.append(f'    label="{c.title.strip()}"')
        #     saida.append(f"    style=filled")
        #     saida.append(f"    color=lightgray")
        #     for q in c.quests:
        #         saida.append(f"    {info(q)}")

        #     saida.append("  }")

        saida.append("}")
        # saida.append("@enduml")
        saida.append("")

        dot_file = self.output + ".dot"
        out_file = self.output + self.graph_ext
        open(dot_file, "w").write("\n".join(saida))

        if self.graph_ext == ".png":
            subprocess.run(["dot", "-Tpng", dot_file, "-o", out_file])
        elif self.graph_ext == ".svg":
            subprocess.run(["dot", "-Tsvg", dot_file, "-o", out_file])
        else:
            print("Formato de imagem não suportado")


class DD:
    cluster_key = "blue, bold"
    cluster_title = "bold"
    quest_key = "blue, bold, italic"
    tasks = "yellow, bold"
    opt = "magenta, italic"
    lcmd = "red, bold"
    cmd = "red"
    code_key = "bold"

    play = "green"
    new = "green, bold"

    nothing = "magenta"
    started = "red"
    required = "yellow"
    complete = "green"

    dots = "yellow" # ...
    shell = "red" # extern shell cmds

    htext = "white"

    check = "green"
    uncheck = "yellow"

    param = "cyan, bold"

class Util:
    @staticmethod
    def calc_letter(index_letter: int):
        unit = index_letter % 26
        ten = index_letter // 26
        if ten == 0:
            return chr(ord("A") + unit)
        return chr(ord("A") + ten - 1) + chr(ord("A") + unit)

    @staticmethod
    def calc_index(letter: str):
        letter = letter.upper()
        if len(letter) == 1:
            return ord(letter) - ord("A")
        return (ord(letter[0]) - ord("A") + 1) * 26 + (ord(letter[1]) - ord("A"))

    @staticmethod
    def get_number(value: int):
        if 0 <= value <= 9:
            return str(value)
        return "*"

    @staticmethod
    def get_percent(value, color2: str = "", pad = 0):
        text = f"{str(value)}%".rjust(pad)
        if value == 100:
            return colour(DD.complete + "," +  color2, "100%")
        if value >= 70:
            return colour(DD.required + "," +  color2, text)
        if value == 0:
            return colour(DD.nothing + "," +  color2, text)
        return colour(DD.started + "," +  color2, text)

    @staticmethod
    def get_term_size():
        return shutil.get_terminal_size().columns
    
    @staticmethod
    def get_num_num(s: str) -> tuple[int | None, int | None]:
        pattern = r"^(\d+)-(\d+)$"
        match = re.match(pattern, s)
        if match:
            return int(match.group(1)), int(match.group(2))
        else:
            return None, None

    @staticmethod
    def get_letter_letter(s: str) -> tuple[str | None, str | None]:
        pattern = r"([a-zA-Z]+)-([a-zA-Z]+)"
        match = re.match(pattern, s)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    @staticmethod
    def expand_range(line: str) -> list[str]:
        line = line.replace(" - ", "-")
        actions = line.split()

        expand: list[str] = []
        for t in actions:
            (start_number, end_number) = Util.get_num_num(t)
            (start_letter, end_letter) = Util.get_letter_letter(t)
            if start_number is not None and end_number is not None:
                expand += [str(v) for v in list(range(start_number, end_number + 1))]
            elif start_letter is not None and end_letter is not None:
                start_index = Util.calc_index(start_letter)
                end_index = Util.calc_index(end_letter)
                limits = range(start_index, end_index + 1)
                expand += [Util.calc_letter(i) for i in limits]
            else:
                expand.append(t)
        return expand
    
    @staticmethod
    def clear():
        subprocess.run("clear")
        pass

    @staticmethod
    def is_number(s):
        try:
            int(s)
            return True
        except ValueError:
            return False


class Play:
    cluster_prefix = "'"

    def __init__(self, local: LocalSettings, game: Game, rep: RepoSettings, repo_alias: str, fnsave):
        self.fnsave = fnsave
        self.local = local
        self.repo_alias = repo_alias
        self.help_options = 0
        self.help_index = 0
        self.rep = rep
        self.show_toolbar = "toolbar" in self.rep.view
        self.admin_mode = "admin" in self.rep.view
        order = [entry for entry in self.rep.view if entry.startswith("order:")]
        if len(order) > 0:
            self.order = order[0][6:].split(",")
        else:
            self.order = []

        self.game: Game = game

        self.vfolds: dict[str, str] = {} # visible collapsers ou expanders for clusters or quests
        self.vtasks: dict[str, Task] = {}  # visible tasks  indexed by upper letter
        self.expanded: list[str] = [x for x in self.rep.expanded]
        self.new_items: list[str] = [x for x in self.rep.new_items]
        self.avaliable_quests: list[Quest] = [] # avaliable quests
        self.avaliable_clusters: list[Cluster] = [] # avaliable clusters

        self.first_loop = True

        self.load_rep()


    def save_to_json(self):
        self.rep.expanded = [x for x in self.expanded]
        self.rep.new_items = [x for x in self.new_items]

        self.rep.tasks = {}
        for t in self.game.tasks.values():
            if t.grade != 0:
                self.rep.tasks[t.key] = str(t.grade)
        self.rep.view = []
        self.rep.view.append("order:" + ",".join(self.order))
        if self.admin_mode:
            self.rep.view.append("admin")
        if self.show_toolbar:
            self.rep.view.append("toolbar")
            
        self.fnsave()


    def load_rep(self):
        for key, grade in self.rep.tasks.items():
            if key in self.game.tasks:
                value = "0"
                if grade == "x":
                    value = "10"
                elif grade == "":
                    value = "0"
                else:
                    value = grade
                self.game.tasks[key].set_grade(int(value))


    # return True if change view
    def update_avaliable_quests(self):
        old_quests = [q for q in self.avaliable_quests]
        old_clusters = [c for c in self.avaliable_clusters]
        if self.admin_mode:
            self.avaliable_quests = list(self.game.quests.values())
            self.avaliable_clusters = self.game.clusters
        else:
            self.avaliable_quests = self.game.get_reachable_quests()
            self.avaliable_clusters = []
            for c in self.game.clusters:
                if any([q in self.avaliable_quests for q in c.quests]):
                    self.avaliable_clusters.append(c)


        removed_clusters = [c for c in old_clusters if c not in self.avaliable_clusters]
        for c in removed_clusters:
            if c.key in self.expanded:
                self.expanded.remove(c.key)
        removed_quests = [q for q in old_quests if q not in self.avaliable_quests]
        for q in removed_quests:
            if q.key in self.expanded:
                self.expanded.remove(q.key)
        
        if self.first_loop:
            self.first_loop = False
            return

        added_clusters = [c for c in self.avaliable_clusters if c not in old_clusters]
        added_quests = [q for q in self.avaliable_quests if q not in old_quests]
        
        for c in added_clusters:
            self.new_items.append(c.key)
        for q in added_quests:
            self.new_items.append(q.key)

    @staticmethod
    def cut_limits(title, fn_gen):
        term_size = Util.get_term_size()
        clear_total = Color.len(fn_gen(title))
        dif = clear_total - term_size
        if dif < 0:
            return fn_gen(title)
        title = title[:-dif - 3] + colour(DD.dots, "...")
        return fn_gen(title)

    def str_task(self, key: str, t: Task, ligc: str, ligq: str, min_value = 1) -> str:
        vindex = colour(DD.tasks, str(key).ljust(2, " "))
        vdone = t.get_grade_symbol(min_value)
        title = t.title

        def gen_saida(_title):
            parts = _title.split(" ")
            if t.opt:
                fn = lambda x: colour(DD.opt, x)
            else:
                fn = lambda x: x
            parts = [("@" + colour(DD.code_key, p[1:]) if p.startswith("@") else fn(p)) for p in parts]

            titlepainted = " ".join(parts)
            return f" {ligc} {ligq}{vindex}{vdone} {titlepainted}"
        
        return Play.cut_limits(title, gen_saida)

    def str_quest(self, key: str, q: Quest, lig: str) -> str:
        key = colour(DD.quest_key, key.rjust(1))

        resume = ""
        for item in self.order:
            if item == "cont":
                resume += " " + q.get_resume_by_tasks()
            elif item == "perc":
                resume += " " + q.get_resume_by_percent().rjust(4)
            elif item == "goal":
                resume += " " + q.get_requirement()

        con = "━─"
        if q.key in self.expanded:
            con = "─┯"
        new = "" if q.key not in self.new_items else colour(DD.new, " [new]")
        def gen_saida(_title):
            if q.opt:
                _title = colour(DD.opt, _title)
            return f" {lig}{con}{key} {_title}{new}{resume}"
        
        return Play.cut_limits(q.title.strip(), gen_saida)

    def str_cluster(self, key: str, cluster: Cluster, quests: list[Quest]) -> str:
        opening = "━─"
        if cluster.key in self.expanded:
            opening = "─┯"

        resume = ""
        for item in self.order:
            if item == "cont":
                resume += " " + cluster.get_resume_by_quests()
            if item == "perc":
                resume += " " + cluster.get_resume_by_percent()

        title = colour(DD.cluster_key, key) + " " + colour(DD.cluster_title, cluster.title.strip())
        new = "" if cluster.key not in self.new_items else colour(DD.new, " [new]")
        return f"{opening}{title}{new}{resume}"
    
    def get_avaliable_quests_from_cluster(self, cluster: Cluster) -> list[Quest]:
        return [q for q in cluster.quests if q in self.avaliable_quests]

    def show_options(self):
        fold_index = 0
        task_index = 0
        self.vfolds = {}
        self.vtasks = {}
        for cluster in self.avaliable_clusters:
            quests = self.get_avaliable_quests_from_cluster(cluster)

            key = str(fold_index)
            self.vfolds[str(key)] = cluster.key
            fold_index += 1
            print(self.str_cluster(key.ljust(2), cluster, quests))
            if not cluster.key in self.expanded: # va para proximo cluster
                continue

            for q in quests:
                key = str(fold_index).ljust(2)
                lig = "├" if q != quests[-1] else "╰"
                print(self.str_quest(key, q, lig))
                self.vfolds[str(fold_index)] = q.key
                fold_index += 1
                if q.key in self.expanded:
                    for t in q.tasks:
                        key = Util.calc_letter(task_index)
                        ligc = "│" if q != quests[-1] else " "
                        ligq = "├─" if t != q.tasks[-1] else "╰─"
                        print(self.str_task(key, t, ligc, ligq, q.tmin))
                        self.vtasks[key] = t
                        task_index += 1

    def process_collapse(self):
        quest_keys = [q.key for q in self.avaliable_quests]
        if any([q in self.expanded for q in quest_keys]):
            self.expanded = [key for key in self.expanded if key not in quest_keys]
        else:
            self.expanded = []

    def process_expand(self):
        # if any cluster outside expanded
        expand_clusters = False
        for c in self.avaliable_clusters:
            if c.key not in self.expanded:
                expand_clusters = True
        if expand_clusters:
            for c in self.avaliable_clusters:
                if c.key not in self.expanded:
                    self.expanded.append(c.key)
        else:
            for q in self.avaliable_quests:
                if q.key not in self.expanded:
                    self.expanded.append(q.key)

    def down_task(self, rootdir, task: Task, ext: str):
        if task.key in task.title:
            cmd = colour(DD.shell, f"tko down {self.repo_alias} {task.key} -l {ext}")
            print(f"{cmd}")
            Down.download_problem(rootdir, self.repo_alias, task.key, ext)
        else:
            print(f"Essa não é uma tarefa de código")

    def check_rootdir(self):
        if self.local.rootdir == "":
            print("Diretório raiz para o tko ainda não foi definido")
            print("Você deseja utilizer o diretório atual")
            print("  " + colour(DD.shell, os.getcwd()))
            print("como raiz para o repositório de " + self.repo_alias + "? (s/n) ", end="")
            answer = input()
            if answer == "s":
                self.local.rootdir = os.getcwd()
                self.fnsave()
                print("Você pode alterar o diretório raiz navegando para o diretório desejado e executando o comando")
                print("  " + colour(DD.shell, "tko config --root"))
            else:
                print("Navegue para o diretório desejado e execute o comando novamente")
                exit(1)
    
    def check_language(self):
        if self.rep.lang == "":
            print("Linguagem de programação default para esse repositório ainda não foi definida")
            print("Escolha a linguagem de programação para o repositório de " + self.repo_alias)
            print("  [c, cpp, py, ts, js, java]: ", end="")
            lang = input()
            self.rep.lang = lang
            self.fnsave()
            print("Você pode mudar a linguagem de programação executando o comando")
            print("  " + colour(DD.cmd, "ext <Extensão>"))

    def process_down(self, actions):
        if len(actions) < 2:
            print("Modo de usar: down <TaskID ...>")
            print("Exemplo: down A C-F")
            return False
        self.check_rootdir()
        self.check_language()

        rootdir = os.path.relpath(os.path.join(self.local.rootdir, self.repo_alias))
        for t in actions[1:]:
            if t in self.vtasks:
                self.down_task(rootdir, self.vtasks[t], self.rep.lang)
            else:
                print(f"Tarefa {t} não encontrada")
                input()

    def find_cluster(self, key) -> Cluster | None:
        for c in self.game.clusters:
            if c.key == key:
                return c
        return None

    def collapse(self, key):
        self.expanded.remove(key)
        cluster = self.find_cluster(key)
        if cluster is not None:
            for q in cluster.quests:
                try:
                    self.expanded.remove(q.key)
                except ValueError:
                    pass

    def process_folds(self, actions):
        mass_action = None
        for t in actions:
            if not Util.is_number(t):
                print(f"Missão '{t}' não é um número")
                return False
            if not str(t) in self.vfolds:
                print(self.vfolds.keys())
                print(f"Entrada '{t}' não existe")
                return False
            key = self.vfolds[str(t)]
            if mass_action is None:
                if key in self.expanded:
                    self.collapse(key)
                    mass_action = "collapse"
                else:
                    self.expanded.append(key)
                    mass_action = "expand"
            else:
                if mass_action == "expand":
                    if key not in self.expanded:
                        self.expanded.append(key)
                else:
                    if key in self.expanded:
                        self.collapse(key)

        return True
    
    def process_tasks(self, actions):
        mass_action: int | None = None
        for t in actions:
            letter = "".join([c for c in t if c.isupper() and not c.isdigit()])
            number = "".join([c for c in t if c.isdigit()])
            if letter in self.vtasks:
                t = self.vtasks[letter]
                if len(number) > 0:
                    t.set_grade(number)
                    continue
                
                if mass_action is not None:
                    t.set_grade(mass_action)
                    continue
                if t.grade == 0:
                    t.set_grade(10)
                    mass_action = 10
                else:
                    t.set_grade(0)
                    mass_action = 0
            else:
                print(f"Talk {t} não processado")
                return False
        return True
    
    
    def process_link(self, actions):
        if len(actions) == 1:
            print("Após o comando passe a letra da tarefa para ver o link")
            return False
        for t in actions[1:]:
            if t in self.vtasks:
                # print(self.tasks[actions[1]].link)
                key = colour(DD.tasks, t)
                link = self.vtasks[t].link
                print(f"{key} {link}")
            else:
                print(f"{t} não processado")
                return False
        return False
    
    def process_ext(self, actions):
        if len(actions) == 1:
            print("Após o comando passe a extensão desejada")
            return False
        ext = actions[1]
        if ext in ["c", "cpp", "py", "ts", "js", "java"]:
            self.rep.lang = ext
            self.fnsave()
            self.reset_view()
            print(f"\nLinguagem de programação alterada para {ext}")
            return False
        else:
            print(f"Extensão {ext} não processada")
            return False

    def take_actions(self, actions) -> bool:
        if len(actions) == 0:
            return True
        cmd = actions[0]

        if cmd == "<":
            self.process_collapse()
        elif cmd == "<<":
            self.process_collapse()
            self.process_collapse()
        elif cmd == ">":
            self.process_expand()
        elif cmd == ">>":
            self.process_expand()
            self.process_expand()
        elif cmd == "h" or cmd == "help":
            return self.show_cmds()
        elif cmd == "c" or cmd == "cont":
            if "cont" in self.order:
                self.order.remove("cont")
            else:
                self.order.append("cont")
        elif cmd == "p" or cmd == "perc":
            if "perc" in self.order:
                self.order.remove("perc")
            else:
                self.order.append("perc")
        elif cmd == "g" or cmd == "goal":
            if "goal" in self.order:
                self.order.remove("goal")
            else:
                self.order.append("goal")
        elif cmd == "a" or cmd == "admin":
            self.admin_mode = not self.admin_mode
        elif cmd == "t" or cmd == "toolbar":
            self.show_toolbar = not self.show_toolbar
        elif cmd == "d" or cmd == "down":
            return self.process_down(actions)
        elif cmd == "l" or cmd == "link":
            return self.process_link(actions)
        elif cmd == "e" or cmd == "ext":
            return self.process_ext(actions)
        elif Util.is_number(cmd):
            return self.process_folds(actions)
        elif cmd[0].isupper():
            return self.process_tasks(actions)
        else:
            print(f"{cmd} não processado")
            return False
        return True

    @staticmethod
    def show_help():
        output = "Digite " + colour(DD.lcmd, "t")
        output += " os números ou intervalo das tarefas para (marcar/desmarcar), exemplo:"
        print(output)
        print(colour(DD.play, "play$ ") + "t 1 3-5")
        return False

    @staticmethod
    def checkbox(value):
        return colour(DD.check, symbols.opcheck) if value else colour(DD.uncheck, symbols.opuncheck)

    def show_header(self):
        Util.clear()
        total_perc = 0
        
        for q in self.game.quests.values():
            total_perc += q.get_percent()
        if self.game.quests:
            total_perc = total_perc // len(self.game.quests)
        
        vrep = colour(DD.htext + ",*", "[")+ colour(DD.tasks, self.repo_alias) + colour(DD.htext + ",*", "]")
        vtotal = colour(DD.htext + ",*", "Total: ") + Util.get_percent(total_perc, "bold", 4)

        intro = vtotal + " " + "│" + colour(DD.htext, " Digite ") + colour(DD.lcmd, "h") + colour(DD.cmd, "elp")
        intro += colour(DD.htext, " ou ") + colour(DD.lcmd, "t") + colour(DD.cmd, "oolbar") 
        intro += Play.checkbox(self.show_toolbar)
        vlink = colour(DD.lcmd, "c") + colour(DD.cmd, "ont") + (Play.checkbox("cont" in self.order))
        vperc = colour(DD.lcmd, "p") + colour(DD.cmd, "erc") + (Play.checkbox("perc" in self.order))
        vgoal = colour(DD.lcmd, "g") + colour(DD.cmd, "oal") + (Play.checkbox("goal" in self.order))

        vadmin = colour(DD.lcmd, "a") + colour(DD.cmd, "dmin") + (Play.checkbox(self.admin_mode))
        
        vext = colour(DD.lcmd, "e") + colour(DD.cmd, "xt") + "(" + colour(DD.param, self.rep.lang) + ")"
        visoes = f"{vrep} {vext} {vlink} {vperc} {vgoal} {vadmin} "


        div0 = "────────────┴─────────────────────────"

        div1 = "──────────────────────────────────────"

        elementos = [intro] + ([div0, visoes] if self.show_toolbar else []) + [div1]
        self.print_elementos(elementos)

    def show_cmds(self):
        controles = colour(DD.htext, "Números ") + colour(DD.cluster_key, "azul") + colour(DD.htext, " para expandir/colapsar")
        letrass = colour(DD.htext, "Letras ") + colour(DD.tasks, "amarelo") + colour(DD.htext, " para marcar/desmarcar")
        intervalos1 = colour(DD.htext, "Você pode digitar intervalos: ") + colour(DD.cluster_key, "1-3")
        intervalos2 = colour(DD.htext, "Você pode digitar intervalos: ") + colour(DD.cluster_key, "B-F")

        numeros = "─┯" + colour(DD.cluster_key, "3") + "  Digite " + colour(DD.cluster_key, "3") + (" para ver ou ocultar")
        
        letras = " ├─" + colour(DD.tasks, "D ") + colour(DD.nothing, symbols.uncheck)
        letras += " Tarefa. Dig " + colour(DD.cluster_key, "D") + " (des)marcar"
        
        graduar = " ╰─" + colour(DD.tasks, "X ") + colour(DD.started, "4")  + " Tarefa. Dig " + colour(DD.cluster_key, "X4") + " dar nota 4"
        todas = colour(DD.cluster_key, "<") + " ou " + colour(DD.cluster_key, ">") + colour(DD.htext, " (Compactar ou Descompactar Tudo)")
        
        nomes_verm = colour(DD.htext, "Os nomes em vermelho são comandos")
        prime_letr = colour(DD.htext, "Basta a primeira letra do comando")
        down = colour(DD.lcmd, "d") + colour(DD.cmd, "own") + colour(DD.param, " <TaskID ...>") + colour(DD.htext, " (Download)")
        link = colour(DD.lcmd, "l") + colour(DD.cmd, "ink") + colour(DD.param, " <TaskID ...>") + colour(DD.htext, " (Ver links)")
        # manu = colour(DD.cmd, "m") + colour(DD.cmd, "an") + yellow("  (Mostrar manual detalhado)")
        ext = colour(DD.lcmd, "e") + colour(DD.cmd, "xt") + colour(DD.param, "  <EXT>") + colour(DD.htext, " (Mudar linguagem default)")
        sair = colour(DD.lcmd, "q") + colour(DD.cmd, "uit") + colour(DD.htext, " (Sair do programa)")
        vcont = colour(DD.lcmd, "c") + colour(DD.cmd, "ont") + colour(DD.htext, " (Alterna contador de tarefas)")
        vperc = colour(DD.lcmd, "p") + colour(DD.cmd, "erc") + colour(DD.htext, " (Alterna mostrar porcentagem)")
        vgoal = colour(DD.lcmd, "g") + colour(DD.cmd, "oal") + colour(DD.htext, " (Alterna mostrar meta mínima)")
        vupdate = colour(DD.lcmd, "u") + colour(DD.cmd, "pdate") + colour(DD.htext, " (Recarrega o arquivo do repositório)")

        # rep = colour(DD.cmd, "r") + colour(DD.cmd, "ep") + colour(DD.htext, " (Muda o repositório)")

        vgame = colour(DD.lcmd, "a") + colour(DD.cmd, "dmin") + colour(DD.htext, " (Liberar todas as missões)")
        # xp = colour(DD.cmd, "x") + red("p") + yellow("  (Mostrar experiência)")
        # indicadores = f"{vall} {vdone} {vinit} {vtodo}"

        div0 = "──────────────────────────────────────"
        div1 = "───────────── " + colour(DD.cluster_key, "Controles") + "──────────────"
        div2 = "───────────── " + colour(DD.lcmd, "Comandos") + " ───────────────"
        elementos = []
        elementos += [div1, controles, letrass, todas, numeros, letras, graduar, intervalos1, intervalos2]
        elementos += [div2, nomes_verm, prime_letr, down, link, ext, vcont, vperc, vgoal, vgame, sair]

        self.print_elementos(elementos)
        print(div0)
        return False

    @staticmethod
    def print_elementos(elementos):
        maxlen = max([len(Color.remove_colors(t)) for t in elementos])
        # qtd = term_size // (maxlen + 3)
        qtd = 1

        count = 0
        for i in range(len(elementos)):
            print(Color.ljust(elementos[i], maxlen), end="")
            count += 1
            if count >= qtd:
                count = 0
                print("")
            elif i < len(elementos) - 1:
                print(" ║ ", end="")
        if count != 0:
            print("")

    def generate_graph(self, graph_ext):

        reachable: list[str] = [q.key for q in self.avaliable_quests]
        counts = {}
        for q in self.game.quests.values():
            done = len([t for t in q.tasks if t.is_complete()])
            init = len([t for t in q.tasks if t.in_progress()])
            todo = len([t for t in q.tasks if t.not_started()])
            counts[q.key] = f"{done} / {done + init + todo}\n{q.get_percent()}%"

        Graph(self.game).set_reachable(reachable).set_counts(counts).set_graph_ext(graph_ext).generate()

    def update_new(self):
        self.new_items = [item for item in self.new_items if item not in self.expanded]


    def reset_view(self):
        self.update_avaliable_quests()
        self.update_new()
        self.show_header()
        self.show_options()


    # return True if the user wants to continue playing
    def play(self, graph_ext: str) -> bool:
        success = True
        first_graph_msg = True 
        while True:
            if success:
                self.reset_view()

            if graph_ext != "":
                self.generate_graph(graph_ext)
                if first_graph_msg:
                    print("\nGrafo gerado em graph" + graph_ext)
                    first_graph_msg = False

            print("\n" + colour(DD.play, "play$") + " ", end="")
            line = input()
            if line == "":
                success = True
                continue
            if line == "q" or line == "quit":
                return False
            if line == "u" or line == "update":
                return True
            actions = Util.expand_range(line)
            success = self.take_actions(actions)
            self.save_to_json()

__version__ = "0.6.2"





class MRep:
    @staticmethod
    def list(_args):
        sp = SettingsParser()
        settings = sp.load_settings()
        print(f"SettingsFile\n- {sp.settings_file}")
        print(str(settings))

    @staticmethod
    def add(args):
        sp = SettingsParser()
        settings = sp.load_settings()
        rep = RepoSettings()
        if args.url:
            rep.set_url(args.url)
        elif args.file:
            rep.set_file(args.file)
        settings.reps[args.alias] = rep
        sp.save_settings()
    
    @staticmethod
    def rm(args):
        sp = SettingsParser()
        settings = sp.load_settings()
        if args.alias in settings.reps:
            settings.reps.pop(args.alias)
            sp.save_settings()
        else:
            print("Repository not found.")

    @staticmethod
    def reset(_args):
        sp = SettingsParser()
        sp.settings = Settings()
        sp.save_settings()

    @staticmethod
    def graph(args):
        sp = SettingsParser()
        settings = sp.load_settings()
        rep = settings.get_repo(args.alias)
        file = rep.get_file()
        game = Game()
        game.parse_file(file)
        game.check_cycle()
        game.generate_graph("graph")


class Main:
    @staticmethod
    def run(args):
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        if args.quiet:
            param.set_diff_mode(DiffMode.QUIET)
        elif args.all:
            param.set_diff_mode(DiffMode.ALL)
        else:
            param.set_diff_mode(DiffMode.FIRST)

        if args.filter:
            param.set_filter(True)
        if args.compact:
            param.set_compact(True)

        # load default diff from settings if not specified
        if not args.sideby and not args.updown:
            local = SettingsParser().load_settings().local
            updown = local.updown
            size_too_short = Report.get_terminal_size() < local.sideto_min
            param.set_up_down(updown or size_too_short)
        elif args.sideby:
            param.set_up_down(False)
        elif args.updown:
            param.set_up_down(True)
        run = Run(args.target_list, args.cmd, param)
        run.execute()

    @staticmethod
    def build(args):
        PatternLoader.pattern = args.pattern
        manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
        build = Build(args.target, args.target_list, manip, args.force)
        build.execute()
    
    @staticmethod
    def settings(args):
        sp = SettingsParser()
        settings = sp.load_settings()
        
        action = False

        if args.ascii:
            action = True
            settings.local.ascii = True
            print("Encoding mode now is: ASCII")
        if args.unicode:
            action = True
            settings.local.ascii = False
            print("Encoding mode now is: UNICODE")
        if args.mono:
            action = True
            settings.local.color = False
            print("Color mode now is: MONOCHROMATIC")
        if args.color:
            action = True
            settings.local.color = True
            print("Color mode now is: COLORED")
        if args.side:
            action = True
            settings.local.updown = False
            print("Diff mode now is: SIDE_BY_SIDE")
        if args.updown:
            action = True
            settings.local.updown = True
            print("Diff mode now is: UP_DOWN")
        if args.lang:
            action = True
            settings.local.lang = args.lang
            print("Default language extension now is:", args.lang)
        if args.ask:
            action = True
            settings.local.lang = ""
            print("Language extension will be asked always.")
            
        if args.root:
            action = True
            settings.local.set_rootdir(".")
            print("Root directory now is: current directory")

        if not action:
            action = True
            print(sp.get_settings_file())
            print(str(settings.local))

        sp.save_settings()

    @staticmethod
    def play(args):
        if args.repo:
            print("playing repo", args.repo)

            while True:
                sp = SettingsParser()
                settings = sp.load_settings()
                repo = settings.get_repo(args.repo)
                local = settings.local
                game = Game()
                file = repo.get_file()
                game.parse_file(file)

                # passing a lambda function to the play class to save the settings
                ext = ""
                if args.graph:
                    ext = ".svg" if args.svg else ".png"
                play = Play(local, game, repo, args.repo, lambda: sp.save_settings())
                reload = play.play(ext)
                if not reload:
                    break

    @staticmethod
    def down(args):
        Down.download_problem(".", args.course, args.activity, args.language)


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='tko', description='A tool for competitive programming.')        
        self.subparsers = self.parser.add_subparsers(title='subcommands', help='help for subcommand.')

        self.parent_manip = None
        self.parent_basic = None

        self.add_parser_global()
        self.add_parent_basic()
        self.add_parent_manip()
        self.add_parser_run()
        self.add_parser_build()
        self.add_parser_down()
        self.add_parser_config()
        self.add_parser_repo()
        self.add_parser_play()

    def add_parser_global(self):
        self.parser.add_argument('-c', metavar='CONFIG_FILE', type=str, help='config json file.')
        self.parser.add_argument('-w', metavar='WIDTH', type=int, help="terminal width.")
        self.parser.add_argument('-v', action='store_true', help='show version.')
        self.parser.add_argument('-g', action='store_true', help='show tko simple guide.')
        self.parser.add_argument('-b', action='store_true', help='show bash simple guide.')
        self.parser.add_argument('-m', action='store_true', help='monochromatic.')
        self.parser.add_argument('-a', action='store_true', help='asc2 mode.')

    def add_parent_basic(self):
        parent_basic = argparse.ArgumentParser(add_help=False)
        parent_basic.add_argument('--index', '-i', metavar="I", type=int, help='run a specific index.')
        parent_basic.add_argument('--pattern', '-p', metavar="P", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')
        self.parent_basic = parent_basic
    
    def add_parent_manip(self):
        parent_manip = argparse.ArgumentParser(add_help=False)
        parent_manip.add_argument('--width', '-w', type=int, help="term width.")
        parent_manip.add_argument('--unlabel', '-u', action='store_true', help='remove all labels.')
        parent_manip.add_argument('--number', '-n', action='store_true', help='number labels.')
        parent_manip.add_argument('--sort', '-s', action='store_true', help="sort test cases by input size.")
        parent_manip.add_argument('--pattern', '-p', metavar="@.in @.out", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')
        self.parent_manip = parent_manip

    def add_parser_run(self):
        parser_r = self.subparsers.add_parser('run', parents=[self.parent_basic], help='run with test cases.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--filter', '-f', action='store_true', help='filter solver in temp dir before run')
        parser_r.add_argument('--compact', '-c', action='store_true', help='Do not show case descriptions in failures')
        parser_r.add_argument("--cmd", type=str, help="bash command to run code")

        group_n = parser_r.add_mutually_exclusive_group()
        group_n.add_argument('--quiet', '-q', action='store_true', help='quiet mode, do not show any failure.')
        group_n.add_argument('--all', '-a', action='store_true', help='show all failures.')

        # add an exclusive group for diff mode
        group = parser_r.add_mutually_exclusive_group()
        group.add_argument('--updown', '-u', action='store_true', help="diff mode up-to-down.")
        group.add_argument('--sideby', '-s', action='store_true', help="diff mode side-by-side.")
        parser_r.set_defaults(func=Main.run)

    def add_parser_build(self):
        parser_b = self.subparsers.add_parser('build', parents=[self.parent_manip], help='build a test target.')
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='target to be build.')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        parser_b.add_argument('--force', '-f', action='store_true', help='enable overwrite.')
        parser_b.set_defaults(func=Main.build)

    def add_parser_down(self):
        parser_d = self.subparsers.add_parser('down', help='download problem from repository.')
        parser_d.add_argument('course', type=str, nargs='?', help=" [ fup | ed | poo ].")
        parser_d.add_argument('activity', type=str, nargs='?', help="activity @label.")
        parser_d.add_argument('--language', '-l', type=str, nargs='?', help="[ c | cpp | js | ts | py | java ]")
        parser_d.set_defaults(func=Main.down)

    def add_parser_config(self):
        parser_s = self.subparsers.add_parser('config', help='settings tool.')

        g_encoding = parser_s.add_mutually_exclusive_group()
        g_encoding.add_argument('--ascii', action='store_true',    help='set ascii mode.')
        g_encoding.add_argument('--unicode', action='store_true', help='set unicode mode.')

        g_color = parser_s.add_mutually_exclusive_group()
        g_color.add_argument('--color', action='store_true', help='set colored mode.')
        g_color.add_argument('--mono',  action='store_true', help='set mono    mode.')

        g_diff = parser_s.add_mutually_exclusive_group()
        g_diff.add_argument('--side', action='store_true', help='set side_by_side diff mode.')
        g_diff.add_argument('--updown', action='store_true', help='set up_to_down   diff mode.')

        g_lang = parser_s.add_mutually_exclusive_group()
        g_lang.add_argument("--lang", '-l', metavar='ext', type=str, help="set default language extension.")
        g_lang.add_argument("--ask", action='store_true', help='ask language extension every time.')
        
        parser_s.add_argument("--root", action='store_true', help='set root directory to current.')

        parser_s.set_defaults(func=Main.settings)

    def add_parser_repo(self):
        parser_repo = self.subparsers.add_parser('rep', help='manipulate repositories.')
        subpar_repo = parser_repo.add_subparsers(title='subcommands', help='help for subcommand.')

        repo_list = subpar_repo.add_parser('list', help='list all repositories')
        repo_list.set_defaults(func=MRep.list)

        repo_add = subpar_repo.add_parser('add', help='add a repository.')
        repo_add.add_argument('alias', metavar='alias', type=str, help='alias of the repository to be added.')
        repo_add.add_argument('--url', '-u', type=str, help='add a repository url to the settings file.')
        repo_add.add_argument('--file', '-f', type=str, help='add a repository file to the settings file.')
        repo_add.set_defaults(func=MRep.add)

        repo_rm = subpar_repo.add_parser('rm', help='remove a repository.')
        repo_rm.add_argument('alias', metavar='alias', type=str, help='alias of the repository to be removed.')
        repo_rm.set_defaults(func=MRep.rm)

        repo_reset = subpar_repo.add_parser('reset', help='reset all repositories to factory default.')
        repo_reset.set_defaults(func=MRep.reset)

        repo_graph = subpar_repo.add_parser('graph', help='generate graph of the repository.')
        repo_graph.add_argument('alias', metavar='alias', type=str, help='alias of the repository to be graphed.')
        repo_graph.set_defaults(func=MRep.graph)

    def add_parser_play(self):
        parser_p = self.subparsers.add_parser('play', help='play a game.')
        parser_p.add_argument('repo', metavar='repo', type=str, help='repository to be played.')
        parser_p.add_argument("--graph", "-g", action='store_true', help='generate graph of the game using graphviz.')
        parser_p.add_argument("--svg", "-s", action='store_true', help='generate graph in svg instead png.')
        parser_p.set_defaults(func=Main.play)

    def main(self):
        args = self.parser.parse_args()

        if len(sys.argv) == 1:
            self.parser.print_help()
            return
        if args.w is not None:
            Report.set_terminal_size(args.width)
        if args.c:
            SettingsParser.user_settings_file = args.c
        settings = SettingsParser().load_settings()
        if args.a or settings.local.ascii:
            symbols.set_ascii()
        else:
            symbols.set_unicode()
        if not args.m and settings.local.color:
            Color.enabled = True
            symbols.set_colors()


        if args.v or args.g or args.b:
            if args.v:
                print("tko version " + __version__)
            if args.b:
                print(bash_guide[1:], end="")
            if args.g:
                print(tko_guide[1:], end="")
        else:
            try:
                args.func(args)
            except ValueError as e:
                print(str(e))


def main():
    try:
        parser = Parser()
        parser.main()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt")
        sys.exit(1)


if __name__ == '__main__':
    main()

