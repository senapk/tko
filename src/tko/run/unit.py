from typing import Optional
from .basic import ExecutionResult
from ..util.ftext import Sentence
import os

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

    def str(self, pad: bool = True) -> Sentence:
        index = str(self.index).zfill(2)
        grade = str(self.grade_reduction).zfill(3)
        rep = "" if self.repeated is None else " [" + str(self.repeated) + "]"
        op = Sentence() + ExecutionResult.get_symbol(self.result) + " " + self.result.value
        source = os.path.basename(self.source)
        if pad:
            source = self.source.ljust(self.source_pad)
        case = self.case
        if pad:
            case = self.case.ljust(self.case_pad)
        return Sentence() + "(" + op + ")" + f"[{index}] GR:{grade} {source} ({case}){rep}"

