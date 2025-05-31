from tko.enums.execution_result import ExecutionResult
from tko.util.text import Text
import os

class Unit:
    def __init__(self, case: str = "", input_data: str = "", expected: str = "", grade: None | int = None, source: str = ""):
        self.source = source  # stores the source file of the unit
        self.source_pad = 0  # stores the pad to justify the source file
        self.case = case  # name
        self.case_pad = 0  # stores the pad to justify the case name
        self.inserted = input_data  # input
        self.__expected = expected  # expected output
        self.__received: None | str = None  # solver generated answer
        self.grade: None | int = grade  # None represents proportional gr, 100 represents all
        self.grade_reduction: int = 0  # if grade is None, this atribute should be filled with the right grade reduction
        self.index = 0
        self.repeated: None | int = None

        self.result: ExecutionResult = ExecutionResult.UNTESTED

    def set_expected(self, expected: str):
        self.__expected = expected.replace("\r", "")
        return self
    
    def get_expected(self) -> str:
        return self.__expected
    
    def set_received(self, received: str):
        self.__received = received.replace("\r", "")
        return self

    def get_received(self) -> None | str:
        return self.__received

    def str(self, pad: bool = True) -> Text:
        index = str(self.index).zfill(2)
        grade = str(self.grade_reduction).zfill(3)
        rep = "" if self.repeated is None else " [" + str(self.repeated) + "]"
        op = Text() + ExecutionResult.get_symbol(self.result) + " " + self.result.value
        source = os.path.basename(self.source)
        if pad:
            source = self.source.ljust(self.source_pad)
        case = self.case
        if pad:
            case = self.case.ljust(self.case_pad)
        return Text() + "(" + op + ")" + f"[{index}] GR:{grade} {source} ({case}){rep}"
