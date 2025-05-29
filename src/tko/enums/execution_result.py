from __future__ import annotations
from tko.util.symbols import symbols
from tko.util.text import Token


import enum


class ExecutionResult(enum.Enum):
    UNTESTED          = "não_verificado_"
    SUCCESS           = "saída_correta__"
    WRONG_OUTPUT      = "saída_incorreta"
    COMPILATION_ERROR = "erro_compilação"
    EXECUTION_ERROR   = "erro_execução__"

    @staticmethod
    def get_symbol(result: ExecutionResult) -> Token:
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

    # @override
    def __str__(self):
        return self.value