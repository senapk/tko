from __future__ import annotations
import shutil
from pathlib import Path


class DraftsFinderCached:
    cache: dict[tuple[Path, str, str], list[Path]] = {}
    
    def __init__(self, task_folder: Path, language: str):
        self.task_folder = task_folder.resolve()
        self.language = language

    @staticmethod
    def reset_cache():
        DraftsFinderCached.cache = {}

    def __get_dir_for_drafts(self) -> Path:
        return self.task_folder / 'src' / self.language

    def __get_dir_for_secondary_drafts(self, count: int) -> Path:
        return self.task_folder / 'src' / f"_{self.language}.{count}"

    @staticmethod
    def __is_source_on(folder: Path, language: str) -> bool:
        if not folder.exists():
            return False
        for file in folder.iterdir():
            if file.suffix == f".{language}":
                return True
        return False

    def find_dir_for_drafts(self) -> Path:
        if self.__is_source_on(self.task_folder, self.language):
            return self.task_folder
        if self.__is_source_on(self.task_folder / self.language, self.language):
            return self.task_folder / self.language
        return self.__get_dir_for_drafts()

    def find_last_secondary_dir_for_drafts(self) -> tuple[Path, int]:
        count = 1
        while True:
            drafts_secondary_folder = self.__get_dir_for_secondary_drafts(count)
            if not drafts_secondary_folder.exists():
                break
            count += 1
        if count == 1:
            return self.__get_dir_for_drafts(), 0
        return self.__get_dir_for_secondary_drafts(count - 1), count - 1

    def find_dir_for_drafts_secondary(self) -> Path:
        _, count = self.find_last_secondary_dir_for_drafts()
        return self.__get_dir_for_secondary_drafts(count + 1)

    def remove_secondary_dir_if_duplicated(self) -> tuple[bool, Path]:
        secondary, _ = self.find_last_secondary_dir_for_drafts()
        if not secondary.exists():
            return False, Path("")
        parts = secondary.name.split(".")
        if len(parts) > 1:
            try:
                count = int(parts[-1])
                if count == 1:
                    last_path = self.__get_dir_for_drafts()
                else:
                    last_path = self.__get_dir_for_secondary_drafts(count - 1)
                if last_path.exists():
                    if self.folder_equals(secondary, last_path):
                        shutil.rmtree(secondary)
                        return True, Path(last_path)
            except ValueError:
                pass
        return False, Path("")

    @staticmethod
    def folder_equals(folder1: Path, folder2: Path) -> bool:
        """ Compare two folders and return if they have the same files with the same content """
        if not folder1.exists() or not folder2.exists():
            return False
        if len(list(folder1.iterdir())) != len(list(folder2.iterdir())):
            return False
        for path1 in folder1.iterdir():
            path2 = folder2 / path1.name
            if not path2.exists() or not path2.is_file():
                return False
            
            with open(path1, "rb") as f1, open(path2, "rb") as f2:
                if f1.read() != f2.read():
                    return False
        return True
    
    def load_source_files(self, extra: list[str] | None = None, cached: bool = False) -> list[Path]:
        if extra is None:
            extra = []
        extra = sorted(extra)
        allowed: list[str] = extra.copy()
        if cached:
            if (self.task_folder, self.language, ":".join(extra)) in self.cache:
                return self.cache[(self.task_folder, self.language, ":".join(extra))]
        if self.language != "":
            allowed.append(self.language)
        if "c" in allowed:
            allowed.append("h")
        if "cpp" in allowed:
            allowed.append("h")
            allowed.append("hpp")
        if not self.task_folder.exists():
            return []
        drafts = self.find_dir_for_drafts()
        if not drafts.exists():
            return []
        draft_list: list[Path] = []
        for file in drafts.iterdir():
            parts = file.parts
            if any([part.startswith("_") for part in parts]):
                continue
            if file.suffix.endswith(tuple(allowed)):
                draft_list.append(file)
        if cached:
            self.cache[(self.task_folder, self.language, ":".join(extra))] = draft_list
        return draft_list