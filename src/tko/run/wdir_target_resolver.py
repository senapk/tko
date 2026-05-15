import os
from pathlib import Path

from tko.cmds.drafts_finder_cached import DraftsFinderCached
from tko.config.settings import Settings
from tko.enums.identifier_type import IdentifierType
from tko.util.identifier import Identifier


class WdirTargetResolver:
    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def normalize_targets(target_list: list[Path]) -> list[Path]:
        if len(target_list) == 0:
            return [Path()]
        return target_list

    @staticmethod
    def resolve_explicit_targets(target_list: list[Path]) -> tuple[list[Path], list[Path]]:
        for target in target_list:
            if not os.path.exists(target):
                raise Warning(f"fail: {target} não encontrado")

        solvers = [target for target in target_list if Identifier.get_type(target.suffix) == IdentifierType.SOLVER]
        sources = [target for target in target_list if Identifier.get_type(target.suffix) != IdentifierType.SOLVER]
        return sources, solvers

    @staticmethod
    def get_autoload_folder(target_list: list[Path]) -> Path | None:
        if len(target_list) == 1 and os.path.isdir(target_list[0]):
            return target_list[0]
        return None

    def resolve_autoload(self, folder: Path, lang: str) -> tuple[list[Path], list[Path]]:
        source_list: list[Path] = [target for target in folder.iterdir() if target.suffix in [".tio", ".vpl", ".toml"]]
        source_list.extend([target for target in folder.iterdir() if target.suffix == ".md"])

        finder = DraftsFinderCached(folder, lang)
        if lang != "":
            solver_list = finder.load_source_files()
        else:
            lang_drafts: list[str] = sorted(self.settings.get_languages_settings().get_languages_with_drafts().keys())
            solver_list = finder.load_source_files(extra=lang_drafts)
        return source_list, sorted(solver_list)