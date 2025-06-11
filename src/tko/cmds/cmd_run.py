import os

from tko.enums.execution_result import ExecutionResult
from tko.run.diff_builder_down import DiffBuilderDown
from tko.run.wdir import Wdir
from tko.enums.diff_count import DiffCount
from tko.util.param import Param
from tko.run.diff_builder_side import DiffBuilderSide
from tko.util.text import Text, Token, aprint

from tko.util.raw_terminal import RawTerminal
from tko.util.symbols import symbols

from tko.util.freerun import Free
from tko.play.tester import Tester
from tko.play.tracker import Tracker
from tko.run.unit_runner import UnitRunner
from tko.game.task import Task
from tko.play.opener import Opener
from tko.settings.settings import Settings
from tko.enums.diff_mode import DiffMode
from tko.settings.logger import Logger
from tko.feno.filter import CodeFilter
from tko.settings.repository import Repository

class tkoFilterMode:
    @staticmethod
    def deep_copy_and_change_dir():
        # path to ~/.tko_filter
        filter_path = os.path.join(os.path.expanduser("~"), ".tko_filter")

        CodeFilter.cf_recursive(".", filter_path, force=True)
        os.chdir(filter_path)

class Run:
    EVAL_MODE_PAD = 14

    def __init__(self, settings: Settings, target_list: list[str], param: None | Param.Basic):
        self.settings = settings
        self.target_list: list[str] = target_list
        if param is None:
            self.param = Param.Basic()
        else:
            self.param = param
        self.wdir: Wdir = Wdir()
        self.wdir_builded = False
        self.__curses_mode: bool = False
        self.__lang = ""
        self.__rep: Repository | None = None
        self.__task: Task | None = None
        self.__track_folder: str = ""
        self.__opener: Opener | None = None
        self.__run_without_ask: bool = True
        self.__show_track_info: bool = False
        self.__show_self_info: bool = False
        self.__eval_mode: bool = False
        self.__complex_percent: bool = False
        self.__abord_on_exec_error: bool = False
        self.__no_run: bool = False
        self.__timeout: int = 0

    def set_eval_mode(self):
        self.__eval_mode = True
        return self

    def show_track_info(self):
        self.__show_track_info = True
        return self
    
    def set_no_run(self):
        self.__no_run = True
        return self
    
    def show_self_info(self):
        self.__show_self_info = True
        return self

    def set_complex_percent(self):
        self.__complex_percent = True
        return self

    def set_abort_on_exec_error(self):
        self.__abord_on_exec_error = True
        return self
    
    def set_timeout(self, timeout: int):
        self.__timeout = timeout
        return self

    def set_curses(self, value:bool=True):
        self.__curses_mode = value
        return self
   
    def set_lang(self, lang:str):
        self.__lang = lang
        return self
    
    def set_opener(self, opener: Opener):
        self.__opener = opener
        return self

    def set_run_without_ask(self, value:bool):
        self.__run_without_ask = value
        return self

    def set_task(self, rep: Repository, task: Task):
        self.__rep = rep
        self.__task = task
        return self
    
    def get_task(self) -> Task:
        if self.__task is None:
            raise Warning("Task não definida")
        return self.__task

    def execute(self):
        if len(self.target_list) == 0:
            self.__try_load_rep(".")
            self.__try_load_task(".")

        elif len(self.target_list) == 1 and os.path.isdir(self.target_list[0]):
            self.__try_load_rep(self.target_list[0])
            self.__try_load_task(self.target_list[0])

        if not self.wdir_builded:
            self.build_wdir()

        if self.__missing_target():
            return 0

        if not self.wdir.has_solver() and self.wdir.has_tests() and not self.__eval_mode:
            self.__list_mode()
            return 0
        
        if self.wdir.has_solver():
            self.__prepare_rep_task_logger()

        if self.wdir.has_solver() and not self.wdir.has_tests() and not self.__curses_mode and not self.__no_run:
            if not self.__eval_mode:
                self.__free_run()
            else:
                aprint(Text().addf("", "fail: ") + "Nenhum caso de teste encontrado.")
            return 0
        
        return self.__run_tests()

    def __prepare_rep_task_logger(self):
        if self.__rep is None:
            solver_path = self.wdir.get_solver().args_list[0]
            dirname = os.path.dirname(os.path.abspath(solver_path))
            self.__try_load_rep(dirname)
            self.__try_load_task(dirname)

        if self.__task is None:
            self.__fill_task()

        if self.__rep is not None:
            logger = Logger.get_instance()
            history_file = self.__rep.get_history_file()
            logger.set_log_files(history_file, self.__rep.get_track_folder())
    
    def __try_load_rep(self, dirname: str) -> bool:
        repo_path = Repository.rec_search_for_repo(dirname)
        if repo_path == "":
            return False
        rep = Repository(repo_path).load_config().load_game()
        self.__rep = rep
        if rep.get_lang() != "":
            self.__lang = rep.get_lang()
        return True

    def __try_load_task(self, dirname: str) -> bool:
        if self.__rep is None:
            return False
        rep: Repository = self.__rep
        task_key = rep.get_key_from_task_folder(dirname)
        if task_key == "":
            return False
        task = rep.game.tasks.get(task_key)
        if task is None:
            return False
        self.__task = task
        self.__track_folder = rep.get_track_task_folder(task_key)
        return True

    def __remove_duplicates(self):
        # remove duplicates in target list keeping the order
        self.target_list = list(dict.fromkeys(self.target_list))

    def __change_targets_to_filter_mode(self):
        if self.param.filter:
            old_dir = os.getcwd()

            aprint(Text.format(" Entrando no modo de filtragem ").center(RawTerminal.get_terminal_size(), Token("═")))
            tkoFilterMode.deep_copy_and_change_dir()  
            # search for target outside . dir and redirect target
            new_target_list: list[str] = []
            for target in self.target_list:
                if ".." in target:
                    new_target_list.append(os.path.normpath(os.path.join(old_dir, target)))
                elif os.path.exists(target):
                    new_target_list.append(target)
            self.target_list = new_target_list
        
    def __print_diff(self):
        
        if self.wdir.get_solver().has_compile_error():
            exec, _ = self.wdir.get_solver().get_executable()
            aprint(exec.get_error_msg())
            return
        
        results = [unit.result for unit in self.wdir.get_unit_list()]
        if ExecutionResult.EXECUTION_ERROR not in results and ExecutionResult.WRONG_OUTPUT not in results:
            return
        
        if not self.param.compact:
            for elem in self.wdir.unit_list_resume():
                aprint(elem)

        if self.param.diff_count == DiffCount.NONE:
            return
        
        if self.param.diff_count == DiffCount.FIRST:
            # printing only the first wrong case
            wrong = [unit for unit in self.wdir.get_unit_list() if unit.result != ExecutionResult.SUCCESS][0]
            if self.param.diff_mode == DiffMode.DOWN:
                ud_diff_builder = DiffBuilderDown(RawTerminal.get_terminal_size(), wrong).to_insert_header()
                for line in ud_diff_builder.build_diff():
                    aprint(line)
            else:
                ss_diff_builder = DiffBuilderSide(RawTerminal.get_terminal_size(), wrong).to_insert_header(True)
                for line in ss_diff_builder.build_diff():
                    aprint(line)
            return

        if self.param.diff_count == DiffCount.ALL:
            for unit in self.wdir.get_unit_list():
                if unit.result != ExecutionResult.SUCCESS:
                    if self.param.diff_mode == DiffMode.DOWN:
                        ud_diff_builder = DiffBuilderDown(RawTerminal.get_terminal_size(), unit).to_insert_header()
                        for line in ud_diff_builder.build_diff():
                            aprint(line)
                    else:
                        ss_diff_builder = DiffBuilderSide(RawTerminal.get_terminal_size(), unit).to_insert_header(True)
                        for line in ss_diff_builder.build_diff():
                            aprint(line)

    def build_wdir(self):
        self.wdir_builded = True
        self.__remove_duplicates()
        self.__change_targets_to_filter_mode()
        try:
            self.wdir = Wdir().set_curses(self.__curses_mode).set_lang(self.__lang).set_target_list(self.target_list).build().filter(self.param)
        except FileNotFoundError as e:
            if self.wdir.has_solver():
                exec, _ = self.wdir.get_solver().get_executable()
                exec.set_compile_error(str(e))
        return self.wdir

    def __missing_target(self) -> bool:
        if not self.wdir.has_solver() and not self.wdir.has_tests():
            if not self.__curses_mode:
                aprint(Text().addf("", "fail: ") + "Nenhum arquivo de código ou de teste encontrado.")
            return True
        return False
    
    def __list_mode(self):
        # list mode
        
        if not self.__eval_mode:
            aprint(Text.format("Nenhum arquivo de código encontrado. Listando casos de teste.").center(RawTerminal.get_terminal_size(), Token("╌")), flush=True)
        aprint(self.wdir.resume_splitted())
        for line in self.wdir.unit_list_resume():
            aprint(line)

    def __free_run(self):        
        if self.__task is not None:
            Logger.get_instance().record_freerun(self.get_task().key)
        Free.free_run(self.wdir.get_solver(), show_compilling=False, to_clear=False, wait_input=False)

    def __create_opener_for_wdir(self) -> Opener:
        opener = Opener(self.settings)
        folders: list[str] = []
        targets = ["."]
        if self.target_list:
            targets = self.target_list
        for f in targets:
            if os.path.isdir(f) and f not in folders:
                folders.append(f)
            else:
                folder = os.path.dirname(os.path.abspath(f))
                if folder not in folders:
                    folders.append(folder)
        opener.set_target(folders)
        if self.wdir.get_solver().args_list:
            solver_zero = self.wdir.get_solver().args_list[0]
            lang = solver_zero.split(".")[-1]
            opener.set_language(lang)
        return opener

    def __fill_task(self):
        task = Task()
        sources = self.wdir.get_source_list()
        solver = self.wdir.get_solver()
        if len(sources) > 0:
            task.folder = os.path.abspath(sources[0])
        elif solver.args_list:
            task.folder = os.path.abspath(self.wdir.get_solver().args_list[0])
        else:
            task.folder = os.path.abspath(os.getcwd())

        if os.path.isfile(task.folder):
            task.folder = os.path.dirname(task.folder)


        task.key = os.path.basename(task.folder)
        self.__task = task
        self.__track_folder = self.__rep.get_track_task_folder(task.key) if self.__rep else ""

    def __run_test_on_curses(self):
        cdiff = Tester(self.settings, self.__rep, self.wdir, self.get_task())
        if self.__opener is not None:
            cdiff.set_opener(self.__opener)
        else:
            cdiff.set_opener(self.__create_opener_for_wdir())
        cdiff.set_autorun(self.__run_without_ask)
        cdiff.run()

    def get_coverage(self) -> int:
        if self.__no_run:
            return 0
        correct = [unit for unit in self.wdir.get_unit_list() if unit.result == ExecutionResult.SUCCESS]
        percent = (len(correct) * 100) // len(self.wdir.get_unit_list())
        return percent

    def __run_tests_on_raw_term(self) -> int:
        if not self.__eval_mode:
            aprint(Text.format(" Testando o código com os casos de teste ").center(RawTerminal.get_terminal_size(), Token("═")))
        percent = self.__run_all_tests_top_line()
        self.__print_diff()
        coverage = self.get_coverage()
        if self.__task is None or self.__track_folder == "" or self.__eval_mode:
            return coverage
        Logger.get_instance().record_test_result(self.get_task().key, coverage)
        tracker = Tracker()
        tracker.set_folder(self.__track_folder)
        tracker.set_files(self.wdir.get_solver().args_list)
        tracker.set_percentage(coverage)
        has_changes, total_lines = tracker.store()
        if has_changes:
            Logger.get_instance().record_file_alteration(self.get_task().key, total_lines)
        return percent

    def __run_tests(self) -> int:
        if self.__task is None:
            self.__fill_task()
        if self.__curses_mode:
            self.__run_test_on_curses()
        else:
            return self.__run_tests_on_raw_term()

        return 0

    def __run_all_tests_top_line(self) -> int:
        if self.__eval_mode:
            key = self.get_task().key if self.__task is not None else ""
            aprint(Text().addf("c", f"@{key:<{self.EVAL_MODE_PAD}} ").add(symbols.opening).add("[").add(self.wdir.resume_join()).add("]"), end="")
        else:
            aprint(Text().add(symbols.opening).add(self.wdir.resume_splitted()), end="")
        aprint(" [", end="")
        first = True
        execution_error = False
        for unit in self.wdir.get_unit_list():
            if first:
                first = False
            else:
                aprint(" ", end="")
            solver = self.wdir.get_solver()
            if self.__no_run or (execution_error and self.__abord_on_exec_error):
                unit.result = ExecutionResult.UNTESTED
            else:
                unit.result = UnitRunner.run_unit(solver, unit, timeout=self.__timeout)
                if unit.result == ExecutionResult.EXECUTION_ERROR:
                    execution_error = True
            aprint(Text() + ExecutionResult.get_symbol(unit.result), end="")
        aprint("] ", end="")
        if self.__show_track_info:
            if self.__rep is not None:
                logger = Logger.get_instance()
                entries = logger.tasks.key_actions.get(self.get_task().key, {})
                if entries:
                    elapsed = max(0, entries[-1].elapsed.total_seconds() // 60)
                    lines = entries[-1].lines
                    if lines == -1:
                        lines = 0
                    attempts = entries[-1].attempts
                    aprint(Text().addf("g", f"min:{elapsed:03.0f}, len:{lines:03d}, att:{attempts:03d},").add(" "), end="", flush=True)

        coverage: int | None = None
        approach: int | None = None
        autonomy: int | None = None
        if self.__show_self_info and self.__rep is not None:
            task: Task | None = self.__rep.game.tasks.get(self.get_task().key)
            if task is not None:
                coverage = task.coverage
                approach = task.approach
                autonomy = task.autonomy
                how_clear = task.how_neat
                how_fun = task.how_cool
                how_easy = task.how_easy
                aprint(Text().addf("m", f"clear:{how_clear}, fun:{how_fun}, easy:{how_easy}, ").addf("y", f"cov:{coverage}, app:{approach}, aut:{autonomy},").add(" "), end="", flush=True)
        if self.__no_run:
            percent: float = 0
        else:
            percent = self.get_coverage()
        if self.__complex_percent:
            if coverage is not None and approach is not None and autonomy is not None:
                if self.__no_run:
                    percent = coverage
                percent = (percent + (((approach + autonomy) * 100) / 11)) / 2

        aprint(f"{percent:03.0f}%")
        return round(percent)