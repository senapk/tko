#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import tempfile
import re
import math
import subprocess
import shutil
import io
import urllib.request
import urllib.error
import json
import argparse
import sys
from enum import Enum
from typing import Optional


class Color(Enum):
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7
    RESET = 8
    BOLD = 9
    ULINE = 10

class Colored:
    __map = {
        Color.RED     : '\u001b[31m',
        Color.GREEN   : '\u001b[32m',
        Color.YELLOW  : '\u001b[33m',
        Color.BLUE    : '\u001b[34m',
        Color.MAGENTA : '\u001b[35m',
        Color.CYAN    : '\u001b[36m',
        Color.WHITE   : '\u001b[37m',
        Color.RESET   : '\u001b[0m',
        Color.BOLD    : '\u001b[1m',
        Color.ULINE   : '\u001b[4m'
    }

    @staticmethod
    def paint(text: str, color: Color, color2: Optional[Color] = None) -> str:
        return Colored.__map[color] + ("" if color2 is None else Colored.__map[color2]) + text + Colored.__map[Color.RESET]

    @staticmethod
    def green(text: str) -> str:
        return Colored.paint(text, Color.GREEN)
    
    @staticmethod
    def red(text: str) -> str:
        return Colored.paint(text, Color.RED)
    
    @staticmethod
    def magenta(text: str) -> str:
        return Colored.paint(text, Color.MAGENTA)

    @staticmethod
    def yellow(text: str) -> str:
        return Colored.paint(text, Color.YELLOW)
    
    @staticmethod
    def blue(text: str) -> str:
        return Colored.paint(text, Color.BLUE)

    @staticmethod
    def ljust(text: str, width: int) -> str:
        return text + ' ' * (width - Colored.len(text))

    @staticmethod
    def center(text: str, width: int, filler) -> str:
        return filler * ((width - Colored.len(text)) // 2) + text + filler * ((width - Colored.len(text) + 1) // 2)

    @staticmethod
    def remove_colors(text: str) -> str:
        for color in Colored.__map.values():
            text = text.replace(color, '')
        return text

    @staticmethod
    def len(text):
        return len(Colored.remove_colors(text))


asc2only: bool = False


class Symbol:
    opening = "=>"
    neutral = ""
    success = ""
    failure = ""
    wrong = ""
    compilation = ""
    execution = ""
    unequal = ""
    equalbar= ""
    hbar = "─"
    vbar = "│"
    whitespace = "\u2E31"  # interpunct
    newline = "\u21B5"  # carriage return
    cfill = "_"
    tab = "    "

    def __init__(self):
        pass

    @staticmethod
    def initialize(asc2only: bool):
        Symbol.neutral = "." if asc2only else "»"  # u"\u2610"  # ☐
        Symbol.success = "S" if asc2only else "✓"
        Symbol.failure = "X" if asc2only else "✗"
        Symbol.wrong = "W" if asc2only else "ω"
        Symbol.compilation = "C" if asc2only else "ϲ"
        Symbol.execution = "E" if asc2only else "ϵ"
        Symbol.unequal = "#" if asc2only else "≠"
        Symbol.equalbar = "|" if asc2only else "│"

        Symbol.opening = Colored.paint(Symbol.opening, Color.BLUE)
        Symbol.neutral = Colored.paint(Symbol.neutral, Color.BLUE)

        Symbol.success = Colored.paint(Symbol.success, Color.GREEN)
        Symbol.failure = Colored.paint(Symbol.failure, Color.RED)
        
        # Symbol.wrong       = Colored.paint(Symbol.wrong,       Color.RED)
        Symbol.compilation = Colored.paint(Symbol.compilation, Color.YELLOW)
        Symbol.execution = Colored.paint(Symbol.execution,   Color.YELLOW)
        Symbol.unequal = Colored.paint(Symbol.unequal,     Color.RED)
        Symbol.equalbar = Colored.paint(Symbol.equalbar,    Color.GREEN)


Symbol.initialize(asc2only)  # inicalizacao estatica

from enum import Enum



class ExecutionResult(Enum):
    UNTESTED = Symbol.neutral
    SUCCESS = Symbol.success
    WRONG_OUTPUT = Symbol.failure
    COMPILATION_ERROR = Symbol.compilation
    EXECUTION_ERROR = Symbol.execution

    def __str__(self):
        return self.value


class DiffMode(Enum):
    FIRST = "MODE: SHOW FIRST FAILURE ONLY"
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

from typing import Optional



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
        self.grade_reduction: int = 0 # if grade is None, this atribute should be filled with the right grade reduction
        self.index = 0
        self.repeated: Optional[int] = None

        self.result: ExecutionResult = ExecutionResult.UNTESTED

    def __str__(self):
        index = str(self.index).zfill(2)
        grade = str(self.grade_reduction).zfill(3)
        rep = "" if self.repeated is None else "[" + str(self.repeated) + "]"
        return "(%s)[%s] GR:%s %s (%s) %s" % (self.result, index, grade, self.source.ljust(self.source_pad), self.case.ljust(self.case_pad), rep)

from typing import Optional



class Param:

    def __init__(self):
        pass

    class Basic:
        def __init__(self):
            self.index: Optional[int] = None
            self.label_pattern: Optional[str] = None
            self.is_up_down: bool = False
            self.diff_mode = DiffMode.FIRST

        def set_index(self, value: Optional[int]):
            self.index: Optional[int] = value
            return self

        def set_label_pattern(self, label_pattern: Optional[str]):
            self.label_pattern: Optional[str] = label_pattern
            return self

        def set_up_down(self, value: bool):
            self.is_up_down = value
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


from typing import List
from shutil import which



def check_tool(name):
    if which(name) is None:
        raise Runner.CompileError("fail: " + name + " executable not found")

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
        check_tool("javac")

        solver = self.path_list[0]
        filename = os.path.basename(solver)
        # tempdir = os.path.dirname(self.path_list[0])
        

        cmd = ["javac"] + self.path_list + ['-d', self.temp_dir]
        return_code, stdout, stderr = Runner.subprocess_run(cmd)
        print(stdout)
        print(stderr)
        if return_code != 0:
            raise Runner.CompileError(stdout + stderr)
        # solver = solver.split(os.sep)[-1]  # getting only the filename
        self.executable = "java -cp " + self.temp_dir + " " + filename[:-5]  # removing the .java

    def __prepare_js(self):
        check_tool("node")

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
        check_tool("esbuild")
        check_tool("node")

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
    
from typing import List, Optional


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

from typing import List, Tuple, Optional


class Loader:
    regex_tio = r"^ *>>>>>>>> *(.*?)\n(.*?)^ *======== *\n(.*?)^ *<<<<<<<< *\n?"

    def __init__(self):
        pass

    @staticmethod
    def parse_cio(text, source, crude_mode=False):
        unit_list = []
        text = "\n" + text

        for test_case in text.split("\n#__case")[1:]:
            unit = Unit()
            unit.source = source
            unit.output = test_case
            unit_list.append(unit)

        for unit in unit_list:
            test = unit.output
            if "\n$end" in test:
                test = test.split("\n$end")[0] + "\n$end"

            lines = test.split("\n")
            tags = lines[0].strip().split(" ")
            if tags[-1].endswith("%"):
                unit.grade = int(tags[-1][0:-1])
                del tags[-1]
            else:
                unit.grade = None
            unit.case = " ".join(tags)
            unit.output = "\n".join(lines[1:])

        # concatenando testes contínuos
        for i in range(len(unit_list)):
            unit = unit_list[i]
            if "\n$end" not in unit.output and (i < len(unit_list) - 1):
                unit_list[i + 1].output = unit.output + '\n' + unit_list[i + 1].output
                unit.output = unit.output + "\n$end\n"

        for unit in unit_list:
            lines = unit.output.split('\n')
            unit.output = ""
            unit.input = ""
            # filtrando linhas vazias e comentários
            for line in lines:
                if crude_mode:  #
                    unit.output += line + '\n'
                    if line == "" or line.startswith("$") or line.startswith("#"):
                        unit.input += line + '\n'
                else:
                    if line != "" and not line.startswith("#"):
                        unit.output += line + '\n'
                        if line.startswith("$"):
                            unit.input += line[1:] + '\n'
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

from typing import List, Optional



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
        solvers = [target for target in target_list if Identifier.get_type(target) == IdentifierType.SOLVER]
        sources = [target for target in target_list if Identifier.get_type(target) != IdentifierType.SOLVER]
        
        self.set_solver(solvers)
        self.set_sources(sources)
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
        return "\n".join([Symbol.tab + str(unit) for unit in self.unit_list])

    def resume(self) -> str:
        def sources() -> str:
            out = []
            if len(self.pack_list) == 0:
                out.append(Symbol.failure)
            for i in range(len(self.pack_list)):
                nome: str = self.source_list[i].split(os.sep)[-1]
                out.append(nome + "(" + str(len(self.pack_list[i])).zfill(2) + ")")
            return Colored.paint("sources:", Color.GREEN) + "[" + ", ".join(out) + "]"

        def solvers() -> str:
            path_list = [] if self.solver is None else self.solver.path_list
            return Colored.paint("solvers:", Color.GREEN) + "[" + ", ".join([os.path.basename(path) for path in path_list]) + "]"

        folder = os.getcwd().split(os.sep)[-1]
        tests_count = Colored.paint("tests:", Color.GREEN) + str(len([x for x in self.unit_list if x.repeated is None])).zfill(2)

        return Symbol.opening + folder + " " + tests_count + " " + sources() + " " + solvers()

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

from subprocess import PIPE
from typing import List, Tuple, Any


class Runner:

    def __init__(self):
        pass

    class CompileError(Exception):
        pass

    @staticmethod
    def subprocess_run(cmd_list: List[str], input_data: str = "") -> Tuple[int, Any, Any]:
        try:
            p = subprocess.Popen(cmd_list, stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
            stdout, stderr = p.communicate(input=input_data)
            return p.returncode, stdout, stderr
        except FileNotFoundError:
            print("\n\nCommand not found: " + " ".join(cmd_list))
            exit(1)



class Execution:

    def __init__(self):
        pass

    # run a unit using a solver and return if the result is correct
    @staticmethod
    def run_unit(solver: Solver, unit: Unit) -> ExecutionResult:
        cmd = solver.executable.split(" ")
        return_code, stdout, stderr = Runner.subprocess_run(cmd, unit.input)
        unit.user = stdout + stderr
        if return_code != 0:
            unit.user += Symbol.execution
            return ExecutionResult.EXECUTION_ERROR
        if unit.user == unit.output:
            return ExecutionResult.SUCCESS
        return ExecutionResult.WRONG_OUTPUT


from typing import Optional


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
    def centralize(text, sep=' ', left_border: Optional[str] = None, right_border: Optional[str] = None) -> str:
        if left_border is None:
            left_border = sep
        if right_border is None:
            right_border = sep
        term_width = Report.get_terminal_size()

        size = Colored.len(text)
        pad = sep if size % 2 == 0 else ""
        tw = term_width - 2
        filler = sep * int(tw / 2 - size / 2)
        return left_border + pad + filler + text + filler + right_border

from typing import List, Optional, Tuple



class Diff:

    @staticmethod
    def render_white(text: Optional[str], color: Optional[Color] = None) -> Optional[str]:
        if text is None:
            return None
        if color is None:
            text = text.replace(' ', Symbol.whitespace)
            text = text.replace('\n', Symbol.newline + '\n')
            return text
        text = text.replace(' ', Colored.paint(Symbol.whitespace, color))
        text = text.replace('\n', Colored.paint(Symbol.newline, color) + '\n')
        return text

    # create a string with both ta and tb side by side with a vertical bar in the middle
    @staticmethod
    def side_by_side(ta: List[str], tb: List[str]):
        cut = (Report.get_terminal_size() // 2) - 1
        upper = max(len(ta), len(tb))
        data = []

        for i in range(upper):
            a = ta[i] if i < len(ta) else "###############"
            b = tb[i] if i < len(tb) else "###############"
            if len(a) < cut:
                a = a.ljust(cut)
            data.append(a + " " + Symbol.vbar + " " + b)

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

        a_render = Diff.render_white(a_text, Color.YELLOW).splitlines()
        b_render = Diff.render_white(b_text, Color.YELLOW).splitlines()

        first_a = get(a_render, first_failure)
        first_b = get(b_render, first_failure)
        greater = max(Colored.len(first_a), Colored.len(first_b))
        lbefore = ""

        if first_failure > 0:
            lbefore = Colored.remove_colors(get(a_render, first_failure - 1))
            greater = max(greater, Colored.len(lbefore))
        
        postext = Report.centralize(Colored.paint(" First line mismatch showing withspaces ", Color.BOLD),  "-") + "\n"
        if first_failure > 0:
            postext += Colored.paint(Colored.ljust(lbefore, greater) + " (previous)", Color.BLUE) + "\n"
        postext += Colored.ljust(first_a, greater) + Colored.paint(" (expected)", Color.GREEN) + "\n"
        postext += Colored.ljust(first_b, greater) + Colored.paint(" (received)", Color.RED) + "\n"
        return postext

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
            cut = (Report.get_terminal_size() // 2) - 1

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
            if i >= a_size or i >= b_size or a_lines[i] != b_lines[i]:
                if first_failure == -1:
                    first_failure = i
                a_output.append(Colored.paint(get(a_lines, i), Color.GREEN))
                b_output.append(Colored.paint(get(b_lines, i), Color.RED))
            else:
                a_output.append(get(a_lines, i))
                b_output.append(get(b_lines, i))

        return a_output, b_output, first_failure

    @staticmethod
    def mount_up_down_diff(unit: Unit) -> str:
        output = io.StringIO()

        string_input = unit.input
        string_expected = unit.output
        string_received = unit.user

        dotted = "-"

        expected_lines, received_lines, first_failure = Diff.render_diff(string_expected, string_received)
        output.write(Report.centralize(Symbol.hbar, Symbol.hbar) + "\n")
        output.write(Report.centralize(str(unit)) + "\n")
        output.write(Report.centralize(Colored.paint(" PROGRAM INPUT ", Color.BLUE), dotted) + "\n")
        output.write(string_input)
        output.write(Report.centralize(Colored.paint(" EXPECTED OUTPUT ", Color.GREEN), dotted) + "\n")
        output.write("\n".join(expected_lines) + "\n")
        output.write(Report.centralize(Colored.paint(" RECEIVED OUTPUT ", Color.RED), dotted) + "\n")
        output.write("\n".join(received_lines) + "\n")
        output.write(Diff.first_failure_diff(string_expected, string_received, first_failure))

        return output.getvalue()

    @staticmethod
    def mount_side_by_side_diff(unit: Unit) -> str:

        def mount_side_by_side(left, right, filler=" ", middle=" "):
            half = int(Report.get_terminal_size() / 2)
            line = ""
            a = " " + Colored.center(left, half - 2, filler) + " "
            if Colored.len(a) > half:
                a = a[:half]
            line += a
            line += middle
            b = " " + Colored.center(right, half - 2, filler) + " "
            if Colored.len(b) > half:
                b = b[:half]
            line += b
            return line

        output = io.StringIO()

        string_input = unit.input
        string_expected = unit.output
        string_received = unit.user

        dotted = "-"
        vertical_separator = Symbol.vbar

        expected_lines, received_lines, first_failure = Diff.render_diff(string_expected, string_received, True)
        output.write(Report.centralize("   ", Symbol.hbar, " ", " ") + "\n")
        output.write(Report.centralize(str(unit)) + "\n")
        input_header = Colored.paint(" INPUT ", Color.BLUE)
        output.write(mount_side_by_side(input_header, input_header, dotted) + "\n")
        output.write(Diff.side_by_side(string_input.splitlines(), string_input.splitlines()) + "\n")
        expected_header = Colored.paint(" EXPECTED OUTPUT ", Color.GREEN)
        received_header = Colored.paint(" RECEIVED OUTPUT ", Color.RED)
        output.write(mount_side_by_side(expected_header, received_header, dotted, vertical_separator) + "\n")
        output.write(Diff.side_by_side(expected_lines, received_lines) + "\n")
        output.write(Diff.first_failure_diff(string_expected, string_received, first_failure))

        return output.getvalue()

from typing import List


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

from typing import List



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
        elif unit.grade != 100:
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

from typing import List


class Replacer:

    def __init__(self):
        pass

    @staticmethod
    def _get_borders(regex, text, options) -> List[str]:
        out = []
        last = 0
        for m in re.finditer(regex, text, options):
            out.append(text[last:m.span()[0]])
            last = m.span()[1]
        out.append(text[last:])
        return out

    @staticmethod
    def _merge_tests(borders, tests):
        out = []
        for i in range(len(borders)):
            out.append(borders[i])
            if i < len(tests):
                out.append(tests[i])
        return out

    @staticmethod
    def insert_tests(regex: str, text: str, options: int, tests: List[str]) -> str:
        borders = Replacer._get_borders(regex, text, options)
        return "".join(Replacer._merge_tests(borders, tests))

from typing import List



class Actions:

    def __init__(self):
        pass

    @staticmethod
    def exec(target_list: List[str]):
        try:
            wdir = Wdir().set_target_list(target_list).build()
        except Runner.CompileError as e:
            print(e)
            return 0
        
        if wdir.solver is None:
            print("\n" + Colored.paint("fail:", Color.RED) + " no solver found\n")
            return        
        
        print(Report.centralize(" Exec " + wdir.solver.executable + " ", Symbol.hbar))
        subprocess.run(wdir.solver.executable, shell=True)

    @staticmethod
    def list(target_list: List[str], param: Param.Basic):
        wdir = Wdir().set_target_list(target_list).build().filter(param)
        print(wdir.resume())
        print(wdir.unit_list_resume())

    @staticmethod
    def run(target_list: List[str], param: Param.Basic) -> int:
        try:
            wdir = Wdir().set_target_list(target_list).build().filter(param)
        except Runner.CompileError as e:
            print(e)
            return 0
        
        print(wdir.resume(), end="")

        if wdir.solver is None:
            print("\n" + Colored.paint("fail:", Color.RED) + " no solver found\n")
            return 0
        
        print("[ ", end="")
        for unit in wdir.unit_list:
            unit.result = Execution.run_unit(wdir.solver, unit)
            print(unit.result.value + " ", end="")
        print("]\n")

        if param.diff_mode != DiffMode.QUIET:        
            results = [unit.result for unit in wdir.unit_list]
            if (ExecutionResult.EXECUTION_ERROR in results) or (ExecutionResult.WRONG_OUTPUT in results):
                print(wdir.unit_list_resume())

                wrong = [unit for unit in wdir.unit_list if unit.result != ExecutionResult.SUCCESS][0]
                if param.is_up_down:
                    print(Diff.mount_up_down_diff(wrong))
                else:
                    print(Diff.mount_side_by_side_diff(wrong))
        return wdir.calc_grade()

    @staticmethod
    def build(target_out: str, source_list: List[str], param: Param.Manip, to_force: bool) -> bool:
        try:
            wdir = Wdir().set_sources(source_list).build()
            wdir.manipulate(param)
            Writer.save_target(target_out, wdir.unit_list, to_force)
        except FileNotFoundError as e:
            print(str(e))
            return False
        return True

from typing import Tuple



class Down:

    @staticmethod
    def update():
        if os.path.isfile(".info"):
            data = open(".info", "r").read().split("\n")[0]
            data = data.split(" ")
            discp = data[0]
            label = data[1]
            ext = data[2]
            Down.entry_unpack(".", discp, label, ext)
        else:
            print("No .info file found, skipping update...")
    
    @staticmethod
    def entry_args(args):
        destiny = Down.create_problem_folder(args.disc, args.index, args.extension)
        Down.entry_unpack(destiny, args.disc, args.index, args.extension)

    @staticmethod
    def create_file(content, path, label=""):
        with open(path, "w") as f:
            f.write(content)
        print(path, label)

    @staticmethod
    def unpack_json(loaded, destiny):
        # extracting all files to folder
        for entry in loaded["upload"]:
            if entry["name"] == "vpl_evaluate.cases":
                Down.compare_and_save(entry["contents"], os.path.join(destiny, "cases.tio"))

        for entry in loaded["keep"]:
            Down.compare_and_save(entry["contents"], os.path.join(destiny, entry["name"]))

        for entry in loaded["required"]:
            path = os.path.join(destiny, entry["name"])
            Down.compare_and_save(entry["contents"], path)


    @staticmethod
    def compare_and_save(content, path):
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(content)
            print(path + " (New)")
        else:
            if open(path).read() != content:
                print(path + " (Updated)")
                with open(path, "w") as f:
                    f.write(content)
            else:
                print(path + " (Unchanged)")
    
    @staticmethod
    def down_problem_def(destiny, cache_url) -> Tuple[str, str]:
        # downloading Readme
        readme = os.path.join(destiny, "Readme.md")
        [tempfile, _content] = urllib.request.urlretrieve(cache_url + "Readme.md")
        Down.compare_and_save(open(tempfile).read(), readme)
        
        # downloading mapi
        mapi = os.path.join(destiny, "mapi.json")
        urllib.request.urlretrieve(cache_url + "mapi.json", mapi)
        return readme, mapi

    @staticmethod
    def create_problem_folder(disc, index, ext):
        # create dir
        destiny = disc + "@" + index
        if not os.path.exists(destiny):
            os.mkdir(destiny)
        else:
            print("problem folder", destiny, "found, merging content.")

        # saving problem info on folder
        info_file = os.path.join(destiny, ".info")
        with open(info_file, "w") as f:
            f.write(disc + " " + index + " " + ext + "\n")
        return destiny

    @staticmethod
    def entry_unpack(destiny, disc, index, ext):
        discp_url = SettingsParser().get_repository(disc)
        if discp_url is None:
            print("discipline not found")
            return
        
        index_url = discp_url + index + "/"
        cache_url = index_url + ".cache/"
        
        # downloading Readme
        try:
            [readme_path, mapi_path] = Down.down_problem_def(destiny, cache_url)
        except urllib.error.HTTPError:
            print("Problem not found")
            return

        with open(mapi_path) as f:
            loaded_json = json.load(f)
        os.remove(mapi_path)
        Down.unpack_json(loaded_json, destiny)

        if len(loaded_json["required"]) == 1: # you already have the students file
            return

        # creating source file for student
        # search if exists a draft file for the extension choosed
        if ext == "-":
            return

        try:
            draft_path = os.path.join(destiny, "draft." + ext)
            urllib.request.urlretrieve(cache_url + "draft." + ext, draft_path)
            print(draft_path + " (Draft) Rename before modify.")
        except urllib.error.HTTPError: # draft not found
            filename = "Solver." if ext == "java" else "solver."
            draft_path = os.path.join(destiny, filename + ext)
            if not os.path.exists(draft_path):
                with open(draft_path, "w") as f:
                    f.write("")
                print(draft_path, "(Empty)")

            return

        # download all files in folder with the same extension or compatible
        # try:
        #     filelist = os.path.join(index, "filelist.txt")
        #     urllib.request.urlretrieve(cache_url + "filelist.txt", filelist)
        #     files = open(filelist, "r").read().splitlines()
        #     os.remove(filelist)

        #     for file in files:
        #         filename = os.path.basename(file)
        #         fext = filename.split(".")[-1]
        #         if fext == ext or ((fext == "h" or fext == "hpp") and ext == "cpp") or ((fext == "h" and ext == "c")):
        #             filepath = os.path.join(index, filename)
        #             # urllib.request.urlretrieve(index_url + file, filepath)
        #             [tempfile, _content] = urllib.request.urlretrieve(index_url + file)
        #             Down.compare_and_save(open(tempfile).read(), filepath)
        # except urllib.error.HTTPError:
        #     return

__version__ = "0.0.2"

# Console scripts




class Main:
    @staticmethod
    def execute(args):
        Actions.exec(args.target_list)

    @staticmethod
    def run(args):
        if args.width is not None:
            Report.set_terminal_size(args.width)
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        if args.quiet:
            param.set_diff_mode(DiffMode.QUIET)
        if args.vertical:
            param.set_up_down(True)
        if Actions.run(args.target_list, param):
            return 0
        return 1

    @staticmethod
    def list(args):
        if args.width is not None:
            Report.set_terminal_size(args.width)
        PatternLoader.pattern = args.pattern
        param = Param.Basic().set_index(args.index)
        Actions.list(args.target_list, param)
        return 0

    @staticmethod
    def build(args):
        if args.width is not None:
            Report.set_terminal_size(args.width)
        PatternLoader.pattern = args.pattern
        manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
        Actions.build(args.target, args.target_list, manip, args.force)
        return 0
    
    @staticmethod
    def settings(args):
        print("settings file at " + SettingsParser().get_settings_file())

    # @staticmethod
    # def rebuild(args):
    #     if args.width is not None:
    #         Report.set_terminal_size(args.width)
    #     PatternLoader.pattern = args.pattern
    #     manip = Param.Manip().set_unlabel(args.unlabel).set_to_sort(args.sort).set_to_number(args.number)
    #     Actions.update(args.target_list, manip, args.cmd)
    #     return 0

    @staticmethod
    def update(_args):
        Down.update()

    @staticmethod
    def main():
        parent_basic = argparse.ArgumentParser(add_help=False)
        # parent_basic.add_argument('--version', '-v', action='version', help='show version.')
        parent_basic.add_argument('--width', '-w', type=int, help="term width")
        parent_basic.add_argument('--index', '-i', metavar="I", type=int, help='run a specific index.')
        parent_basic.add_argument('--pattern', '-p', metavar="P", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')

        parent_manip = argparse.ArgumentParser(add_help=False)
        parent_manip.add_argument('--width', '-w', type=int, help="term width.")
        parent_manip.add_argument('--unlabel', '-u', action='store_true', help='remove all labels.')
        parent_manip.add_argument('--number', '-n', action='store_true', help='number labels.')
        parent_manip.add_argument('--sort', '-s', action='store_true', help="sort test cases by input size.")
        parent_manip.add_argument('--pattern', '-p', metavar="@.in @.out", type=str, default='@.in @.sol',
                                  help='pattern load/save a folder, default: "@.in @.sol"')

        parser = argparse.ArgumentParser(prog='tko', description='A tool for competitive programming.')
        subparsers = parser.add_subparsers(title='subcommands', help='help for subcommand.')

        # list
        parser_l = subparsers.add_parser('list', parents=[parent_basic], help='show case packs or folders.')
        parser_l.add_argument('target_list', metavar='T', type=str, nargs='*', help='targets.')
        parser_l.set_defaults(func=Main.list)

        # exec
        parser_e = subparsers.add_parser('exec', parents=[parent_basic], help='just run the solver without any test.')
        parser_e.add_argument('target_list', metavar='T', type=str, nargs='*', help='target.')
        parser_e.set_defaults(func=Main.execute)

        # run
        parser_r = subparsers.add_parser('run', parents=[parent_basic], help='run you solver.')
        parser_r.add_argument('target_list', metavar='T', type=str, nargs='*', help='solvers, test cases or folders.')
        parser_r.add_argument('--vertical', '-v', action='store_true', help="use vertical mode.")
        parser_r.add_argument('--quiet', '-q', action='store_true', help='quiet mode, do not show diffs')
        parser_r.set_defaults(func=Main.run)

        # build
        parser_b = subparsers.add_parser('build', parents=[parent_manip], help='build a test target.')
        parser_b.add_argument('target', metavar='T_OUT', type=str, help='target to be build.')
        parser_b.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        parser_b.add_argument('--force', '-f', action='store_true', help='enable overwrite.')
        parser_b.set_defaults(func=Main.build)

        # # rebuild
        # parser_rb = subparsers.add_parser('rebuild', parents=[parent_manip], help='rebuild a test target.')
        # parser_rb.add_argument('target_list', metavar='T', type=str, nargs='+', help='input test targets.')
        # parser_rb.add_argument('--cmd', '-c', type=str, help="solver file or command to update outputs.")
        # parser_rb.set_defaults(func=Main.rebuild)

        # down
        parser_d = subparsers.add_parser('down', help='download test from remote repository.')
        parser_d.add_argument('disc', type=str, help=" [ fup | ed | poo ]")
        parser_d.add_argument('index', type=str, help="3 digits label like 021")
        parser_d.add_argument('extension', type=str, nargs = '?', default = "-", help="[ c | cpp | js | ts | py | java ]")
        parser_d.set_defaults(func=Down.entry_args)

        # update
        parser_u = subparsers.add_parser('update', help='update problem from repository.')
        parser_u.set_defaults(func=Main.update)

        # settings
        parser_s = subparsers.add_parser('settings', help='show settings.')
        parser_s.set_defaults(func=Main.settings)

        args = parser.parse_args()
        if len(sys.argv) == 1:
            print("You must call a subcommand. Use --help for more information.")
        else:
            try:
                args.func(args)
            except ValueError as e:
                print(str(e))


if __name__ == '__main__':
    try:
        Main.main()
    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt")

