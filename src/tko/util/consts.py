import enum

from .symbols import symbols
from .sentence import Token

class ExecutionResult(enum.Enum):
    UNTESTED          = "não  testado   "
    SUCCESS           = "saída correta  "
    WRONG_OUTPUT      = "saída errada   "
    COMPILATION_ERROR = "erro compilação"
    EXECUTION_ERROR   = "erro execução  "

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

class DiffMode(enum.Enum): # não mude os valores pois são utilizados no json
    SIDE = "side"
    DOWN = "down"

class DiffCount(enum.Enum):
    FIRST = "MODO: APENAS PRIMEIRO ERRO"
    ALL   = "MODO: TODOS OS ERROS"
    QUIET = "MODO: SILENCIOSO"


class IdentifierType(enum.Enum):
    OBI = "OBI"
    MD = "MD"
    TIO = "TIO"
    VPL = "VPL"
    SOLVER = "SOLVER"

class Success(enum.Enum):
    RANDOM = "RANDOM"
    FIXED = "FIXED"
