from pathlib import Path

from tko.game.quest_parser import QuestParser
from tko.game.task_parser import TaskParser
from tko.game.quest import Quest
from tko.game.task import Task
from tko.settings.rep_source import RepSource
from tko.util.decoder import Decoder
from tko.feno.indexer import fix_readme
from icecream import ic # type: ignore

class GameBuilder:
    def __init__(self, source: RepSource):
        self.source = source
        self.ordered_quests: list[str] = [] # ordered quests keys
        self.quests: dict[str, Quest] = {}
        self.active_quest: Quest | None = None
        # self.unique_keys: set[str] = set()
        self.interactive: bool = False

    def set_interactive(self, interactive: bool):
        self.interactive = interactive
        return self

    def build_from(self, language: str):
        try:
            filename: Path = self.source.get_source_readme()
        except ValueError as e:
            print(f"Erro ao obter o arquivo README da fonte {self.source.name}: {e}")
            return self
        self.__ensure_sandbox_readme_fixed(filename)
        content: str = self.load_content(filename)
        self.__parse_file_content(content)
        quest_filters, task_filters = self.source.get_filters()
        self.__remove_empty_and_other_language_and_filtered(language, quest_filters, task_filters) 
        self.__create_requirements_pointers()
        self.__create_cross_references()
        return self

    def load_content(self, filename: Path) -> str:
        content: str = ""
        if not filename.exists():
            if not self.source.is_sandbox_source():
                print(f"Aviso: fonte {filename} não encontrada no source {self.source.name}")
        else:
            content = Decoder.load(filename)
        return content

    def __ensure_sandbox_readme_fixed(self, filename: Path):
        if not self.source.is_sandbox_source():
            return
        if not filename.parent.exists():
            return
        if not filename.exists():
            # print(f"Aviso: fonte {filename} não encontrada no source {self.source.name}, criando arquivo")
            filename.parent.mkdir(parents=True, exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# {self.source.name}\n\n")
        fix_readme(filename.resolve(), self.source.get_workspace(), self.source.name, verbose=False, load_titles=True)


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
                    quests[r].required_by_ptr.append(q)
                else:
                    print(f"Quest\n{filename}:{q.line_number}\n{str(q)}\nrequer {r} que não existe")
                    exit(1)


    # def __parse_folder_for_tasks(self, database_path: Path):
    #     alias = self.source.name
    #     if not os.path.exists(database_path):
    #         os.makedirs(database_path)
    #     for task_path in database_path.iterdir():
    #         if not task_path.is_dir():
    #             continue
    #         if not (task_path / "README.md").exists():
    #             continue
    #         print("debug", f"Loading task from folder {task_path}")
    #         self.add_task_from_folder(alias, task_path)

    #     self.__get_active_quest().sort_tasks_by_title()

    # def add_task_from_folder(self, alias: str, task_dir_path: Path):
    #     task = Task()
    #     key = task_dir_path.name
    #     keys = [t.get_key() for t in self.__get_active_quest().get_tasks()]
    #     # print("debug", f"Adding task from folder {task_dir_path}, key: {key}, existing keys: {keys}")
    #     if key in keys:
    #         print("debug", f"Duplicate key {key} in {task_dir_path}")
    #         return
    #     task.set_key(key)
    #     task.set_title(TaskLine.load_markdown_title_or_first_line(task_dir_path / "README.md"))
    #     task.set_remote_name(alias)
    #     task.set_origin_folder(Path(task_dir_path))
    #     if self.source.is_read_only():
    #         task.set_workspace_folder(self.source.get_task_workspace(key))
    #     self.__add_task(task)

    
    # def __load_sandbox_tasks(self):
    #     if self.source.is_sandbox_source():
    #         sandbox_folder = self.source.get_source_workspace()
    #         self.__add_quest(Quest(self.source.name, f"{self.source.name}").set_remote_name(self.source.name))
    #         print("debug", f"Loading sandbox tasks from {sandbox_folder}")
    #         self.__parse_folder_for_tasks(sandbox_folder)

    def __parse_file_content(self, content: str):
        lines = content.splitlines()
        alias = self.source.name
        filename = self.source.get_source_readme()

        for line_num, line in enumerate(lines):
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
        if quest.get_full_key() not in self.quests:
            # print("debug", f"Adding quest {quest.get_full_key()} with title {quest.get_title()}")
            self.quests[quest.get_full_key()] = quest
        if quest.get_full_key() not in self.ordered_quests:
            self.ordered_quests.append(quest.get_full_key())
        self.active_quest = quest
        return quest

    def __add_task(self, task: Task):
        self.__get_active_quest().add_task(task)

    def add_filtered_quests(self, quest_filters: dict[str, str] | None):
        if self.source.is_sandbox_source():
            return
        if quest_filters is None or len(quest_filters) == 0:
            return
        quests: list[Quest] = []
        available_quests = [q for q in self.quests.values()]
        for pattern, destiny in quest_filters.items():
            for q in available_quests:
                if (pattern.lower() in q.get_title().lower()) or (pattern.lower() == f"@{q.get_key()}".lower()):
                    if destiny == "":
                        quests.append(q)
                    else:
                        qdestiny = self.quests.get(f"{self.source.name}@{destiny}", None)
                        if qdestiny is None:
                            qdestiny = Quest(destiny, destiny).set_remote_name(self.source.name)
                            self.__add_quest(qdestiny)
                        for t in q.get_tasks():
                            qdestiny.add_task(t)
                        if qdestiny not in quests:
                            quests.append(qdestiny)
        self.quests = {q.get_full_key(): q for q in quests}

    def filter_by_language_and_empty(self, language: str):
        quests: list[Quest] = []
        for q in self.quests.values():
            if len(q.get_tasks()) == 0:
                continue
            if len(q.languages) == 0 or language in q.languages:
                quests.append(q)
        self.quests = {q.get_full_key(): q for q in quests}
        return self

    def __remove_empty_and_other_language_and_filtered(self, language: str, quest_filters: dict[str, str] | None, task_filters: dict[str, str] | None):
        if quest_filters is None or len(quest_filters) == 0:
            self.filter_by_language_and_empty(language)
        else:
            self.add_filtered_quests(quest_filters)
        return self

    def __create_cross_references(self): #call after clear_empty
        for quest in self.quests.values():
            quest.remote_name = self.source.name
            for task in quest.get_tasks():
                task.remote_name = self.source.name
                task.quest_key = quest.get_full_key()