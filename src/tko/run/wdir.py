from tko.run.unit import Unit
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
    pt="Você não definiu os arquivos diretamente. Use [y]-l[] caso queira especificar a linguagem para autoloading.",
    en="You did not define files directly. Use [y]-l[] if you want to specify the language for autoloading.",
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
        self.solver: None | SolverBuilder = None
        self.source_list: list[Path] = []
        self.pack_list: list[list[Unit]] = []
        self.unit_list: list[Unit] = []
        self.curses_mode: bool = False
        self.lang: str | None = None
        self.autoload_folder: Path | None = None


    def get_solver(self) -> SolverBuilder:
        if self.solver is None:
            raise ValueError(t(_RUN_NO_SOURCE_FILES))
        return self.solver

    @property
    def has_tests(self) -> bool:
        return len(self.unit_list) != 0

    def setup_solver(self, solver_list: list[Path]):
        if len(solver_list) > 0:
            self.solver = SolverBuilder(solver_list, self.settings)
        return self
    
    def autoload(self):
        if self.autoload_folder is None:
            raise ValueError(t(_RUN_AUTOLOAD_FOLDER_NOT_SET) + " " + t(_RUN_AUTOLOAD_LANG_HINT))
        source_list, solver_list = WdirTargetResolver.resolve_autoload(self.autoload_folder, self.lang)
        self.setup_solver(solver_list)
        self.source_list = source_list

    def setup_from_target_list(self, target_list: list[Path]) -> None:
        target_list = WdirTargetResolver.normalize_targets(target_list)
        if len(target_list) == 1 and target_list[0].is_dir():
            self.autoload_folder = target_list[0]
            self.autoload()
            return
        
        sources, solvers = WdirTargetResolver.identify_source_and_solver_targets(target_list)
        self.setup_solver(solvers)
        self.source_list = sources

    def build_unit_list(self):
        self.pack_list, loading_failures = WdirUnitsService.load_packs(self.source_list)
        if loading_failures > 0 and loading_failures == len(self.source_list):
            raise FileNotFoundError(t(_RUN_NO_TEST_CASES))
        self.unit_list = WdirUnitsService.merge_unique_units(self.pack_list)
        #self.__number_and_mark_duplicated()
        #self.__remove_duplicated()
        WdirUnitsService.calculate_grade_reduction(self.unit_list)
        WdirUnitsService.pad_units(self.unit_list)
        return self

    def calc_grade(self) -> int:
        return WdirUnitsService.calc_grade(self.unit_list)

    # select a single unit to execute exclusively
    def filter(self, param: Param.Basic):
        index = param.index
        if index is not None:
            if 0 <= index < len(self.unit_list):
                self.unit_list = [self.unit_list[index]]
            else:
                raise ValueError(t(_RUN_FILTER_INDEX_OUT_OF_BOUNDS, index=index))
        return self

    def manipulate(self, param: Param.Manip):
        self.unit_list = WdirManipulationService.apply(self.unit_list, param)

    def unit_list_resume(self) -> list[RT]:
        return WdirSummaryService.unit_list_resume(self.unit_list)

    def sources_names(self) -> list[tuple[str, str]]:
        return WdirSummaryService.sources_names(self.source_list, self.pack_list)

    def solvers_names(self) -> list[str]:
        return WdirSummaryService.solvers_names(self.solver)

    def resume_splitted(self) -> RT:
        return WdirSummaryService.resume_splitted(self.source_list, self.pack_list, self.solver)

    def resume_join(self) -> RT:
        return WdirSummaryService.resume_join(self.source_list, self.pack_list, self.solver)
