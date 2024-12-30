import enum

from .symbols import symbols
from .text import Token

class ExecutionResult(enum.Enum):
    UNTESTED          = "não_verificado_"
    SUCCESS           = "saída_correta__"
    WRONG_OUTPUT      = "saída_incorreta"
    COMPILATION_ERROR = "erro_compilação"
    EXECUTION_ERROR   = "erro_execução__"

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
