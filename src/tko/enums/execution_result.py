from __future__ import annotations
from tko.util.symbols import Symbols
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
            return Text.Token(Symbols.neutral)
        elif result == ExecutionResult.SUCCESS:
            return Text.Token(Symbols.success)
        elif result == ExecutionResult.WRONG_OUTPUT:
            return Text.Token(Symbols.wrong)
        elif result == ExecutionResult.COMPILATION_ERROR:
            return Text.Token(Symbols.compilation)
        elif result == ExecutionResult.EXECUTION_ERROR:
            return Text.Token(Symbols.execution)
        else:
            raise ValueError("Invalid result type")

    # @override
    def __str__(self):
        return self.value