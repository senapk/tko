import enum
from typing import Optional
import os

from ..util.symbols import symbols
from ..util.ftext import Token, Sentence

class CompilerError(Exception):
    pass

class ExecutionResult(enum.Enum):
    UNTESTED = "untested_"
    SUCCESS = "correct__"
    WRONG_OUTPUT = "wrong_out"
    COMPILATION_ERROR = "compilati"
    EXECUTION_ERROR = "execution"

    @staticmethod
    def get_symbol(result) -> Token:
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

