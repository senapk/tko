from tko.run.solver_builder import SolverBuilder
from tko.run.unit import Unit
from tko.util.rt import RT
from tko.util.symbols import Symbols

from pathlib import Path


class WdirSummaryService:
    @staticmethod
    def unit_list_resume(unit_list: list[Unit]) -> list[RT]:
        return [unit.str() for unit in unit_list]

    @staticmethod
    def sources_names(source_list: list[Path], pack_list: list[list[Unit]]) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        if len(pack_list) == 0:
            out.append((Symbols.failure, "0"))
        for source_name, unit_list in zip(source_list, pack_list):
            name: str = source_name.name
            count = len([unit for unit in unit_list if unit.repeated is None])
            if count > 0:
                count_str = str(count)
                total = len(unit_list)
                if count < total:
                    count_str += "/" + str(total)
                out.append((name, count_str))
        return out

    @staticmethod
    def solvers_names(solver: SolverBuilder | None) -> list[str]:
        path_list = [] if solver is None else solver.args_list
        if solver is not None and len(path_list) == 0:
            return ["free cmd"]
        return [path.name for path in path_list]

    @staticmethod
    def resume_splitted(source_list: list[Path], pack_list: list[list[Unit]], solver: SolverBuilder | None) -> RT:
        sources = ["{}({})".format(name, str(count).rjust(2, "0")) for name, count in WdirSummaryService.sources_names(source_list, pack_list)]
        source_text = RT("Testes:[") + RT(", ".join(sources), "y") + "]"
        solver_text = RT("Códigos:[") + RT(", ".join(WdirSummaryService.solvers_names(solver)), "g") + "]"
        return solver_text + " " + source_text

    @staticmethod
    def resume_join(source_list: list[Path], pack_list: list[list[Unit]], solver: SolverBuilder | None) -> RT:
        sources = ["{}({})".format(name, str(count).rjust(2, "0")) for name, count in WdirSummaryService.sources_names(source_list, pack_list)]
        source_text = RT(", ".join(sources), "y")
        solver_text = RT(", ".join(WdirSummaryService.solvers_names(solver)), "g")
        return solver_text + ", " + source_text