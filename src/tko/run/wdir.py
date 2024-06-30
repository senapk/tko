from typing import List, Optional
import math
import os

from .basic import IdentifierType, Identifier, Unit, Param
from .loader import Loader
from .solver import Solver

from ..util.term_color import colour
from ..util.symbols import symbols

# generate label for cases


class LabelFactory:
    def __init__(self):
        self._label = ""
        self._index = -1

    def index(self, value: int):
        try:
            self._index = int(value)
        except ValueError:
            raise ValueError("Index on label must be a integer")
        return self

    def label(self, value: str):
        self._label = value
        return self

    def generate(self):
        label = LabelFactory.trim_spaces(self._label)
        label = LabelFactory.remove_old_index(label)
        if self._index != -1:
            index = str(self._index).zfill(2)
            if label != "":
                return index + " " + label
            else:
                return index
        return label

    @staticmethod
    def trim_spaces(text):
        parts = text.split(" ")
        parts = [word for word in parts if word != '']
        return " ".join(parts)

    @staticmethod
    def remove_old_index(label):
        split_label = label.split(" ")
        if len(split_label) > 0:
            try:
                int(split_label[0])
                return " ".join(split_label[1:])
            except ValueError:
                return label


class Wdir:
    def __init__(self):
        self.solver: Optional[Solver] = None
        self.source_list: List[str] = []
        self.pack_list: List[List[Unit]] = []
        self.unit_list: List[Unit] = []

    def set_solver(self, solver_list: List[str]):
        if len(solver_list) > 0:
            self.solver = Solver(solver_list)
        return self

    def set_sources(self, source_list: List[str]):
        self.source_list = source_list
        return self

    def set_target_list(self, target_list: List[str]):
        target_list = [t for t in target_list if t != ""]
        for target in target_list:
            if not os.path.exists(target):
                raise FileNotFoundError(colour("red", "fail: ") + target + " not found")

        solvers = [target for target in target_list if Identifier.get_type(target) == IdentifierType.SOLVER]
        sources = [target for target in target_list if Identifier.get_type(target) != IdentifierType.SOLVER]
        
        self.set_solver(solvers)
        self.set_sources(sources)
        return self

    def set_cmd(self, exec_cmd: Optional[str]):
        if exec_cmd is None:
            return self
        if self.solver is not None:
            print("fail: if using --cmd, don't pass source files to target")
        self.solver = Solver([])
        self.solver.executable = exec_cmd
        return self

    def build(self):
        loading_failures = 0
        for source in self.source_list:
            try:
                self.pack_list.append(Loader.parse_source(source))
            except FileNotFoundError as e:
                print(str(e))
                loading_failures += 1
                pass
        if loading_failures > 0 and loading_failures == len(self.source_list):
            raise FileNotFoundError("failure: none source found")
        self.unit_list = sum(self.pack_list, [])
        self.__number_and_mark_duplicated()
        self.__calculate_grade()
        self.__pad()
        return self

    def calc_grade(self) -> int:
        grade = 100
        for case in self.unit_list:
            if not case.repeated and (case.user is None or case.output != case.user):
                grade -= case.grade_reduction
        return max(0, grade)

    # put all the labels with the same length
    def __pad(self):
        if len(self.unit_list) == 0:
            return
        max_case = max([len(x.case) for x in self.unit_list])
        max_source = max([len(x.source) for x in self.unit_list])
        for unit in self.unit_list:
            unit.case_pad = max_case
            unit.source_pad = max_source

    # select a single unit to execute exclusively
    def filter(self, param: Param.Basic):
        index = param.index
        if index is not None:
            if 0 <= index < len(self.unit_list):
                self.unit_list = [self.unit_list[index]]
            else:
                raise ValueError("Index Number out of bounds: " + str(index))
        return self

    # calculate the grade reduction for the cases without grade
    # the grade is proportional to the number of unique cases
    def __calculate_grade(self):
        unique_count = len([x for x in self.unit_list if not x.repeated])
        for unit in self.unit_list:
            if unit.grade is None:
                unit.grade_reduction = math.floor(100 / unique_count)
            else:
                unit.grade_reduction = unit.grade

    # number the cases and mark the repeated
    def __number_and_mark_duplicated(self):
        new_list = []
        index = 0
        for unit in self.unit_list:
            unit.index = index
            index += 1
            search = [x for x in new_list if x.input == unit.input]
            if len(search) > 0:
                unit.repeated = search[0].index
            new_list.append(unit)
        self.unit_list = new_list

    # sort, unlabel ou rename using the param received
    def manipulate(self, param: Param.Manip):
        # filtering marked repeated
        self.unit_list = [unit for unit in self.unit_list if unit.repeated is None]
        if param.to_sort:
            self.unit_list.sort(key=lambda v: len(v.input))
        if param.unlabel:
            for unit in self.unit_list:
                unit.case = ""
        if param.to_number:
            number = 00
            for unit in self.unit_list:
                unit.case = LabelFactory().label(unit.case).index(number).generate()
                number += 1

    def unit_list_resume(self):
        return "\n".join([str(unit) for unit in self.unit_list])

    def resume(self) -> str:

        def sources() -> str:
            out = []
            if len(self.pack_list) == 0:
                out.append(symbols.failure)
            for i in range(len(self.pack_list)):
                nome: str = self.source_list[i].split(os.sep)[-1]
                out.append(nome + "(" + str(len(self.pack_list[i])).zfill(2) + ")")
            return colour("green", "base:") + "[" + ", ".join(out) + "]"

        def solvers() -> str:
            path_list = [] if self.solver is None else self.solver.path_list

            if self.solver is not None and len(path_list) == 0:  # free_cmd
                out = "free cmd"
            else:
                out = ", ".join([os.path.basename(path) for path in path_list])
            return colour("green", "prog:") + "[" + out + "]"

        # folder = os.getcwd().split(os.sep)[-1]
        # tests_count = (colour("tests:", Color.GREEN) +
        #               str(len([x for x in self.unit_list if x.repeated is None])).zfill(2))

        return symbols.opening + sources() + " " + solvers()
