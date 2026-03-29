from pathlib import Path

from tko.game.quest_parser import QuestParser
from tko.game.task_parser import TaskParser
from tko.game.quest import Quest
from tko.game.task import Task
from tko.settings.rep_source import RepSource, AUTOLOAD_COMMAND
from tko.util.decoder import Decoder
import os
from icecream import ic # type: ignore

class GameBuilder:
    def __init__(self, source: RepSource):
        self.source = source
        self.ordered_quests: list[str] = [] # ordered quests keys
        self.quests: dict[str, Quest] = {}
        self.active_quest: Quest | None = None
        self.unique_keys: set[str] = set()
        self.interactive: bool = False

    def set_interactive(self, interactive: bool):
        self.interactive = interactive
        return self

    def build_from(self, language: str):
        filename: Path = self.source.get_source_readme()
        content: str = ""
        if not filename.exists():
            print(f"Aviso: fonte {filename} não encontrada no source {self.source.name}")
        else:
            content = Decoder.load(filename)
        self.__parse_file_content(content)
        self.__clear_empty_or_other_language(language)
        self.__create_requirements_pointers()
        self.__create_cross_references()
        return self


    def collect_tasks(self) -> dict[str, Task]:
        tasks: dict[str, Task] = {}

        for quest in self.quests.values():
            for task in quest.get_tasks():
                tasks[task.get_full_key()] = task
        return tasks

    def collect_quests(self) -> dict[str, Quest]:
        quests: dict[str, Quest] = {}
        for quest in self.quests.values():
            quests[quest.get_full_key()] = quest
        return quests

    def __create_requirements_pointers(self):
        quests, tasks = self.source.get_filters()
        if quests is not None or tasks is not None:
            return

        filename: Path = self.source.get_source_readme()
        quests = self.collect_quests()
        # verificar se todas as quests requeridas existem e adicionar o ponteiro
        for q in quests.values():
            for r in q.requires:
                if r in quests:
                    q.requires_ptr.append(quests[r])
                else:
                    # print(f"keys: {self.quests.keys()}")
                    print(f"Quest\n{filename}:{q.line_number}\n{str(q)}\nrequer {r} que não existe")
                    exit(1)


    def __parse_quest_folder(self, database_path: Path):
        alias = self.source.name
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        for task_path in database_path.iterdir():
            if not task_path.is_dir():
                continue
            if not (task_path / "README.md").exists():
                continue
            
            self.create_task_from_folder(alias, task_path)

    def create_task_from_folder(self, alias: str, task_dir_path: Path):
        task = Task()
        key = task_dir_path.name

        task.set_key(key)
        task.set_title(self.load_markdown_title_or_first_line(task_dir_path / "README.md"))
        task.set_remote_name(alias)
        task.set_origin_folder(Path(task_dir_path))
        if self.source.is_read_only():
            task.set_workspace_folder(self.source.get_task_workspace(key))
        self.__add_task(task)

    def load_markdown_title_or_first_line(self, path: Path) -> str:
        if not path.exists():
            return ""
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("---"):
                    continue
                if len(line.split(":")) > 1:
                    continue
                line = line.strip()
                if line.startswith("#"):
                    return line.lstrip("#").strip()
                if line.strip() != "":
                    return line
        return ""

    def __is_autoload_cmd(self, line: str) -> Path | None:
        words = line.split(f"{AUTOLOAD_COMMAND}=")
        if len(words) == 2:
            path: str = words[1].strip("-> ")
            readme_folder = self.source.get_source_readme().parent
            folder = Path(readme_folder) / path
            return folder
        return None
    

    def __parse_file_content(self, content: str):
        lines = content.splitlines()
        alias = self.source.name
        filename = self.source.get_source_readme()
        for line_num, line in enumerate(lines):
            sandbox_folder = self.__is_autoload_cmd(line)
            if sandbox_folder:
                self.__add_quest(Quest(sandbox_folder.name, f"{sandbox_folder.name}").set_remote_name(alias))
                self.__parse_quest_folder(sandbox_folder)

            quest_parser = QuestParser(alias)
            quest = quest_parser.parse_quest(filename, line, line_num + 1)
            if quest is not None:
                self.__add_quest(quest_parser.finish_quest())
                continue

            tp = TaskParser(filename, alias)
            task = tp.parse_line(line, line_num + 1).check_path_try().get_task()
            if task is not None:
                if self.source.is_read_only() and not task.is_link():
                    task.set_workspace_folder(self.source.get_task_workspace(task.get_key()))
                self.__add_task(task)

    def __get_active_quest(self) -> Quest:
        if self.active_quest is None:
            qkey = "_sem_quest"
            return self.__add_quest(Quest("Sem Quest", qkey))
        return self.active_quest

    def __add_quest(self, quest: Quest) -> Quest:
        self.quests[quest.get_full_key()] = quest
        self.ordered_quests.append(quest.get_full_key())
        self.active_quest = quest
        return quest

    def __add_task(self, task: Task):
        self.__get_active_quest().add_task(task)


    def remove_empty_and_other_language_and_filtered(self, language: str, quest_filters: list[str] | None, task_filters: list[str] | None):
        # self.__quests = [q for q in self.__quests if len(q.get_tasks()) > 0]
        quests: list[Quest] = []
        for q in self.quests.values():
            if len(q.get_tasks()) == 0:
                continue
            if quest_filters is not None and len(quest_filters) > 0:
                allow = False
                for filter in quest_filters:
                    if filter.lower() in q.get_title().lower() or filter.lower() in q.get_full_key().lower():
                        allow = True
                        break
                if not allow:
                    continue
            if len(q.languages) == 0 or language in q.languages:
                quests.append(q)
        self.quests = {q.get_full_key(): q for q in quests}

        return self

    def __clear_empty_or_other_language(self, language: str): #call before create_cross_references
        # apagando quests vazias da lista de quests
        quest_filters, task_filters = self.source.get_filters()
        self.remove_empty_and_other_language_and_filtered(language, quest_filters, task_filters) 

    def __create_cross_references(self): #call after clear_empty
        for quest in self.quests.values():
            quest.remote_name = self.source.name
            for task in quest.get_tasks():
                task.remote_name = self.source.name
                task.quest_key = quest.get_full_key()