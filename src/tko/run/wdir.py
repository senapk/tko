from tko.run.unit import Unit
from tko.run.wdir_config import WdirConfig
from tko.run.wdir_manipulation_service import WdirManipulationService
from tko.util.param import Param
from tko.run.solver_builder import SolverBuilder
from tko.run.wdir_summary_service import WdirSummaryService
from tko.run.wdir_target_resolver import WdirTargetResolver
from tko.run.wdir_units_service import WdirUnitsService
from tko.i18n import Msg, t
from tko.util.rt import RT
from pathlib import Path
from tko.config.settings import Settings


_RUN_NO_SOURCE_FILES = Msg(
    pt="Nenhum arquivo de código encontrado.",
    en="No source files found.",
)
_RUN_AUTOLOAD_FOLDER_NOT_SET = Msg(
    pt="fail: pasta de autoload não definida",
    en="fail: autoload folder is not set",
)
_RUN_AUTOLOAD_LANG_HINT = Msg(
    pt="Você não definiu os arquivos diretamente. Use <-l:y> caso queira especificar a linguagem para autoloading.",
    en="You did not define files directly. Use <-l:y> if you want to specify the language for autoloading.",
)
_RUN_NO_TEST_CASES = Msg(
    pt="Nenhum caso de teste encontrado.",
    en="No test cases found.",
)
_RUN_FILTER_INDEX_OUT_OF_BOUNDS = Msg(
    pt="Índice fora dos limites: {index}",
    en="Index out of bounds: {index}",
)

class Wdir:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.__config = WdirConfig()
        self.__solver: None | SolverBuilder = None
        self.__source_list: list[Path] = []
        self.__pack_list: list[list[Unit]] = []
        self.__unit_list: list[Unit] = []
        self.__summary_service = WdirSummaryService()
        self.__target_resolver = WdirTargetResolver(self.settings)
        self.__manipulation_service = WdirManipulationService()
        self.__units_service = WdirUnitsService()

    def has_solver(self) -> bool:
        return not self.__solver is None

    def has_tests(self) -> bool:
        return len(self.__unit_list) != 0

    def get_solver(self) -> SolverBuilder:
        if self.__solver is None:
            raise FileNotFoundError(t(_RUN_NO_SOURCE_FILES))
        return self.__solver
    
    def get_unit_list(self) -> list[Unit]:
        return self.__unit_list

    def get_unit(self, index: int) -> Unit:
        return self.__unit_list[index]
    
    def get_source_list(self) -> list[Path]:
        return self.__source_list

    def set_curses(self, value: bool):
        self.__config.set_curses(value)
        return self

    def set_lang(self, lang: str):
        self.__config.set_lang(lang)
        return self
    
    def is_curses(self) -> bool:
        return self.__config.curses_mode

    def is_autoload(self) -> bool:
        return self.__config.autoload

    def get_autoload_folder(self) -> Path | None:
        return self.__config.autoload_folder

    def set_solver(self, solver_list: list[Path]):
        if len(solver_list) > 0:
            self.__solver = SolverBuilder(solver_list, self.settings)
        return self

    def set_sources(self, source_list: list[Path]):
        self.__source_list = source_list
        return self

    def autoload(self):
        if self.__config.autoload_folder is None:
            raise Warning(t(_RUN_AUTOLOAD_FOLDER_NOT_SET))
        folder: Path = self.__config.autoload_folder

        if self.__config.lang == "":
            print(RT.parse(t(_RUN_AUTOLOAD_LANG_HINT)))

        source_list, solver_list = self.__target_resolver.resolve_autoload(folder, self.__config.lang)

        self.set_solver(solver_list)
        self.set_sources(source_list)
        self.__config.set_autoload(True)
        return self

    def set_target_list(self, target_list: list[Path]):
        target_list = self.__target_resolver.normalize_targets(target_list)
        autoload_folder = self.__target_resolver.get_autoload_folder(target_list)
        if autoload_folder is not None:
            self.__config.set_autoload_folder(autoload_folder)
            return self.autoload()

        sources, solvers = self.__target_resolver.resolve_explicit_targets(target_list)

        self.set_solver(solvers)
        self.set_sources(sources)
        return self

    def build(self):
        self.__pack_list, loading_failures = self.__units_service.load_packs(self.__source_list)
        if loading_failures > 0 and loading_failures == len(self.__source_list):
            raise FileNotFoundError(t(_RUN_NO_TEST_CASES))
        self.__unit_list = self.__units_service.merge_unique_units(self.__pack_list)
        #self.__number_and_mark_duplicated()
        #self.__remove_duplicated()
        self.__units_service.calculate_grade_reduction(self.__unit_list)
        self.__units_service.pad_units(self.__unit_list)
        return self

    def calc_grade(self) -> int:
        return self.__units_service.calc_grade(self.__unit_list)

    # select a single unit to execute exclusively
    def filter(self, param: Param.Basic):
        index = param.index
        if index is not None:
            if 0 <= index < len(self.__unit_list):
                self.__unit_list = [self.__unit_list[index]]
            else:
                raise ValueError(t(_RUN_FILTER_INDEX_OUT_OF_BOUNDS, index=index))
        return self

    def manipulate(self, param: Param.Manip):
        self.__unit_list = self.__manipulation_service.apply(self.__unit_list, param)

    def unit_list_resume(self) -> list[RT]:
        return self.__summary_service.unit_list_resume(self.__unit_list)

    def sources_names(self) -> list[tuple[str, str]]:
        return self.__summary_service.sources_names(self.__source_list, self.__pack_list)

    def solvers_names(self) -> list[str]:
        return self.__summary_service.solvers_names(self.__solver)

    def resume_splitted(self) -> RT:
        return self.__summary_service.resume_splitted(self.__source_list, self.__pack_list, self.__solver)

    def resume_join(self) -> RT:
        return self.__summary_service.resume_join(self.__source_list, self.__pack_list, self.__solver)
