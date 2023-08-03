from enum import Enum
import os

from .symbol import Symbol


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
