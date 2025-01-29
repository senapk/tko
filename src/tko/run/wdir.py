from typing import List, Optional, Tuple
import math
import os

from tko.util.identifier import Identifier

from tko.util.consts import IdentifierType
from tko.run.unit import Unit
from tko.util.param import Param
from tko.run.loader import Loader
from tko.run.solver_builder import SolverBuilder

from tko.down.drafts import Drafts
from tko.util.text import Text
from tko.util.symbols import symbols
from tko.util.label_factory import LabelFactory
from tko.settings.repository import available_languages
class Wdir:
    def __init__(self):
        self.__autoload = False
        self.__autoload_folder = ""
        self.__solver: Optional[SolverBuilder] = None
        self.__source_list: List[str] = []
        self.__pack_list: List[List[Unit]] = []
        self.__unit_list: List[Unit] = []
        self.__curses = False
        self.__lang = ""

    def has_solver(self) -> bool:
        return not self.__solver is None

    def has_tests(self) -> bool:
        return len(self.__unit_list) != 0

    def get_solver(self) -> SolverBuilder:
        if self.__solver is None:
            raise Warning("fail: Não foi encontrado arquivo de código")
        return self.__solver
    
    def get_unit_list(self) -> List[Unit]:
        return self.__unit_list

    def get_unit(self, index: int) -> Unit:
        return self.__unit_list[index]
    
    def get_source_list(self) -> List[str]:
        return self.__source_list

    def set_curses(self, value: bool):
        self.__curses = value
        return self

    def set_lang(self, lang: str):
        self.__lang = lang
        return self
    
    def is_curses(self) -> bool:
        return self.__curses

    def is_autoload(self) -> bool:
        return self.__autoload

    def get_autoload_folder(self) -> str:
        return self.__autoload_folder

    def set_solver(self, solver_list: List[str]):
        if len(solver_list) > 0:
            self.__solver = SolverBuilder(solver_list)
        return self

    def set_sources(self, source_list: List[str]):
        self.__source_list = source_list
        return self

    def autoload(self):
        folder = self.__autoload_folder
        folder = os.path.normpath(os.path.abspath(folder))

        # loading source list
        files = os.listdir(folder)
        source_list = [target for target in files if target.endswith(".tio") or target.endswith(".vpl") or target.endswith(".cases")]
        if len(source_list) == 0:
            source_list = [target for target in files if target.endswith(".md")]
        source_list = [os.path.join(folder, x) for x in source_list]
        
        solver_list: list[str] = []
        if self.__lang != "":
            solver_list = Drafts.load_drafs(folder, self.__lang)
        solver_list = sorted(solver_list)

        # if not self.__curses:
        #     print("códigos encontrados: [" + ", ".join(solvers) + "]")
        #     print("testes  encontrados: [" + ", ".join(sources) + "]")
        #     print("Para remover um arquivo da lista, renomeie para sua extensão para .txt")
        self.set_solver(solver_list)
        self.set_sources(source_list)
        self.__autoload = True
        return self

    def set_target_list(self, target_list: List[str]):
        target_list = [os.path.normpath(t) for t in target_list]
        if len(target_list) == 0:
            target_list.append(".")
        if len(target_list) == 1 and os.path.isdir(target_list[0]):
            self.__autoload_folder = target_list[0]
            return self.autoload()
                    
        target_list = [t for t in target_list if t != ""]
        for target in target_list:
            if not os.path.exists(target):
                raise Warning(f"fail: {target} não encontrado")

        solvers = [target for target in target_list if Identifier.get_type(target) == IdentifierType.SOLVER]
        sources = [target for target in target_list if Identifier.get_type(target) != IdentifierType.SOLVER]

        self.set_solver(solvers)
        self.set_sources(sources)
        return self

    def build(self):
        loading_failures = 0
        self.__pack_list = []
        for source in self.__source_list:
            try:
                self.__pack_list.append(Loader.parse_source(source))
            except FileNotFoundError as e:
                print(str(e))
                loading_failures += 1
                pass
        if loading_failures > 0 and loading_failures == len(self.__source_list):
            raise FileNotFoundError("failure: nenhum arquivo de teste encontrado")
        self.__unit_list = sum(self.__pack_list, [])
        self.__number_and_mark_duplicated()
        self.__calculate_grade()
        self.__pad()
        return self

    def calc_grade(self) -> int:
        grade = 100
        for case in self.__unit_list:
            if not case.repeated and (case.received is None or case.expected != case.received):
                grade -= case.grade_reduction
        return max(0, grade)

    # put all the labels with the same length
    def __pad(self):
        if len(self.__unit_list) == 0:
            return
        max_case = max([len(x.case) for x in self.__unit_list])
        max_source = max([len(x.source) for x in self.__unit_list])
        for unit in self.__unit_list:
            unit.case_pad = max_case
            unit.source_pad = max_source

    # select a single unit to execute exclusively
    def filter(self, param: Param.Basic):
        index = param.index
        if index is not None:
            if 0 <= index < len(self.__unit_list):
                self.__unit_list = [self.__unit_list[index]]
            else:
                raise ValueError("Índice fora dos limites: " + str(index))
        return self

    # calculate the grade reduction for the cases without grade
    # the grade is proportional to the number of unique cases
    def __calculate_grade(self):
        unique_count = len([x for x in self.__unit_list if not x.repeated])
        for unit in self.__unit_list:
            if unit.grade is None:
                unit.grade_reduction = math.floor(100 / unique_count)
            else:
                unit.grade_reduction = unit.grade

    # number the cases and mark the repeated
    def __number_and_mark_duplicated(self):
        new_list: List[Unit] = []
        index = 0
        for unit in self.__unit_list:
            unit.index = index
            index += 1
            search = [x for x in new_list if x.inserted == unit.inserted]
            if len(search) > 0:
                unit.repeated = search[0].index
            new_list.append(unit)
        self.__unit_list = new_list

    # sort, unlabel ou rename using the param received
    def manipulate(self, param: Param.Manip):
        # filtering marked repeated
        self.__unit_list = [unit for unit in self.__unit_list if unit.repeated is None]
        if param.to_sort:
            self.__unit_list.sort(key=lambda v: len(v.inserted))
        if param.unlabel:
            for unit in self.__unit_list:
                unit.case = ""
        if param.to_number:
            number = 00
            for unit in self.__unit_list:
                unit.case = LabelFactory().label(unit.case).index(number).generate()
                number += 1

    def unit_list_resume(self) -> List[Text]:
        return [unit.str() for unit in self.__unit_list]

    def sources_names(self) -> List[Tuple[str, int]]:
        out: List[Tuple[str, int]] = []
        if len(self.__pack_list) == 0:
            out.append((symbols.failure.text, 0))
        for i in range(len(self.__pack_list)):
            nome: str = self.__source_list[i].split(os.sep)[-1]
            out.append((nome, len(self.__pack_list[i])))
        return out

    def solvers_names(self) -> List[str]:
        path_list = [] if self.__solver is None else self.__solver.path_list
        if self.__solver is not None and len(path_list) == 0:  # free_cmd
            out = ["free cmd"]
        else:
            out = [os.path.basename(path) for path in path_list]
        return out

    def resume(self) -> Text:
        sources = ["{}({})".format(name, str(count).rjust(2, "0")) for name, count in self.sources_names()]
        __sources = Text().add("Testes:").add("[").addf("y", ", ".join(sources)).add("]")

        __solvers = Text().add("Códigos:").add("[").addf("g", ", ".join(self.solvers_names())).add("]")

        return Text().add(__solvers).add(" ").add(__sources)
