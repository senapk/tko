from __future__ import annotations
from tko.i18n import Msg
from tko.util.symbols import Symbols
from tko.util.rt import RT
import enum


_EXECUTION_RESULT_INVALID_TYPE = Msg(
    pt="Invalid result type",
    en="Invalid result type",
)

class ExecutionResult(enum.Enum):
    UNTESTED          = "não_verificado_"
    SUCCESS           = "saída_correta__"
    WRONG_OUTPUT      = "saída_incorreta"
    COMPILATION_ERROR = "erro_compilação"
    EXECUTION_ERROR   = "erro_execução__"

    @staticmethod
    def get_symbol(result: ExecutionResult) -> RT:
        if result == ExecutionResult.UNTESTED:
            return RT(Symbols.neutral)
        elif result == ExecutionResult.SUCCESS:
            return RT(Symbols.success)
        elif result == ExecutionResult.WRONG_OUTPUT:
            return RT(Symbols.wrong)
        elif result == ExecutionResult.COMPILATION_ERROR:
            return RT(Symbols.compilation)
        elif result == ExecutionResult.EXECUTION_ERROR:
            return RT(Symbols.execution)
        else:
            raise ValueError(str(_EXECUTION_RESULT_INVALID_TYPE))

    # @override
    def __str__(self):
        return self.value