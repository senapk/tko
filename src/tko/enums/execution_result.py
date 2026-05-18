from __future__ import annotations
from tko.i18n import Msg, t
from tko.util.symbols import Symbols
from tko.util.rtext import RText
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
    def get_symbol(result: ExecutionResult) -> RText:
        if result == ExecutionResult.UNTESTED:
            return RText(Symbols.neutral)
        elif result == ExecutionResult.SUCCESS:
            return RText(Symbols.success)
        elif result == ExecutionResult.WRONG_OUTPUT:
            return RText(Symbols.wrong)
        elif result == ExecutionResult.COMPILATION_ERROR:
            return RText(Symbols.compilation)
        elif result == ExecutionResult.EXECUTION_ERROR:
            return RText(Symbols.execution)
        else:
            raise ValueError(t(_EXECUTION_RESULT_INVALID_TYPE))

    # @override
    def __str__(self):
        return self.value