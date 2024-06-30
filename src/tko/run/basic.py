import enum
from typing import Optional
import os

from ..util.symbols import symbols

class CompilerError(Exception):
    pass

class ExecutionResult(enum.Enum):
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


class DiffMode(enum.Enum):
    FIRST = "MODE: SHOW FIRST FAILURE ONLY"
    ALL = "MODE: SHOW ALL FAILURES"
    QUIET = "MODE: SHOW NONE FAILURES"


class IdentifierType(enum.Enum):
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
        source = self.source.ljust(self.source_pad)
        case = self.case.ljust(self.case_pad)
        return f"({op})[{index}] GR:{grade} {source} ({case}) {rep}"


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
