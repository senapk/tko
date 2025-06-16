from __future__ import annotations
from tko.util.symbols import symbols
from tko.util.text import Text

import enum

class ExecutionResult(enum.Enum):
    UNTESTED          = "não_verificado_"
    SUCCESS           = "saída_correta__"
    WRONG_OUTPUT      = "saída_incorreta"
    COMPILATION_ERROR = "erro_compilação"
    EXECUTION_ERROR   = "erro_execução__"

    @staticmethod
    def get_symbol(result: ExecutionResult) -> Text.Token:
        if result == ExecutionResult.UNTESTED:
            return symbols.execution_result["untested"]
        elif result == ExecutionResult.SUCCESS:
            return symbols.execution_result["success"]
        elif result == ExecutionResult.WRONG_OUTPUT:
            return symbols.execution_result["wrong_output"]
        elif result == ExecutionResult.COMPILATION_ERROR:
            return symbols.execution_result["compilation_error"]
        elif result == ExecutionResult.EXECUTION_ERROR:
            return symbols.execution_result["execution_error"]
        else:
            raise ValueError("Invalid result type")

    # @override
    def __str__(self):
        return self.value