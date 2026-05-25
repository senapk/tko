from pathlib import Path

from tko.cmds.drafts_finder_cached import DraftsFinderCached
# from tko.enums.identifier_type import IdentifierType
from tko.i18n import Msg, t
from tko.loader.loader import Loader

_RUN_TARGET_NOT_FOUND = Msg(
    pt="fail: {target} não encontrado",
    en="fail: {target} not found",
)


class WdirTargetResolver:
    @staticmethod
    def normalize_targets(target_list: list[Path]) -> list[Path]:
        if len(target_list) == 0:
            return [Path()]
        return target_list

    @staticmethod
    def identify_source_and_solver_targets(target_list: list[Path]) -> tuple[list[Path], list[Path]]:
        for target in target_list:
            if not target.exists():
                raise Warning(t(_RUN_TARGET_NOT_FOUND, target=target))

        solvers = [target for target in target_list if target.suffix not in Loader.SOURCES_EXTENSIONS]
        sources = WdirTargetResolver.filter_and_order_sources([target for target in target_list if not target in solvers])
        return sources, solvers


    @staticmethod
    def resolve_autoload(folder: Path, lang: str | None) -> tuple[list[Path], list[Path]]:
        source_list: list[Path] = WdirTargetResolver.filter_and_order_sources([target for target in folder.iterdir()])
        if lang is not None:
            finder = DraftsFinderCached(folder, lang)
            solver_list: list[Path] = finder.load_source_files()
            return source_list, sorted(solver_list)
        return source_list, []
    
    @staticmethod
    def filter_and_order_sources(files: list[Path]):
        output: list[Path] = []
        for ext in Loader.SOURCES_EXTENSIONS:
            for f in files:
                if f.suffix == ext:
                    output.append(f)
        return output
