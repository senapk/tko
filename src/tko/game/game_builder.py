from pathlib import Path
import logging

from tko.game.quest_parser import QuestParser
from tko.game.task_parser import TaskParser
from tko.game.quest import Quest
from tko.game.task import Task
from tko.repository.remote import Remote
from tko.util.decoder import Decoder
from tko.feno.indexer import fix_readme
from tko.i18n import Msg, t
from icecream import ic  # type: ignore


logger = logging.getLogger(__name__)

_GAME_BUILDER_README_FETCH_ERROR = Msg(
    pt="Erro ao obter o arquivo README da fonte {name}",
    en="Error fetching README file from source {name}",
)
_GAME_BUILDER_SOURCE_NOT_FOUND = Msg(
    pt="Aviso: fonte {filename} não encontrada no source {name}",
    en="Warning: source {filename} not found in source {name}",
)
_GAME_BUILDER_SOURCE_NOT_FOUND_CREATING = Msg(
    pt="Aviso: fonte {filename} não encontrada no source {name}, criando arquivo",
    en="Warning: source {filename} not found in source {name}, creating file",
)
_GAME_BUILDER_QUEST_REQUIRES_MISSING = Msg(
    pt="Quest\n{filename}:{line}\n{quest}\nrequer {required} que não existe",
    en="Quest\n{filename}:{line}\n{quest}\nrequires {required} that does not exist",
)
_GAME_BUILDER_SOURCE_NO_ORIGIN_DIR = Msg(
    pt="Aviso: fonte {name} não possui diretório de origem",
    en="Warning: source {name} has no source directory",
)
_GAME_BUILDER_INDEX_FETCH_ERROR = Msg(
    pt="Erro ao obter o arquivo de índice da fonte {name}",
    en="Error fetching index file from source {name}",
)
_GAME_BUILDER_NO_QUEST_TITLE = Msg(
    pt="Sem Quest",
    en="No Quest",
)


class GameBuilder:
    def __init__(self, remote: Remote, verbose: bool):
        self.remote: Remote = remote
        self.ordered_quests: list[str] = []  # ordered quests keys
        self.quests: dict[str, Quest] = {}
        self.active_quest: Quest | None = None
        self.interactive: bool = False
        self.verbose: bool = verbose

    def set_interactive(self, interactive: bool):
        self.interactive = interactive
        return self

    def build_from(self, language: str):
        try:
            filename: Path = self.remote.path.index_file
            if self.verbose and not self.remote.is_sandbox and not filename.exists():
                logger.exception(t(_GAME_BUILDER_README_FETCH_ERROR, name=self.remote.data.name))
        except ValueError:
            if self.verbose and not self.remote.is_sandbox:
                logger.exception(t(_GAME_BUILDER_SOURCE_NO_ORIGIN_DIR, name=self.remote.data.name))
            return self
        self.__ensure_sandbox_readme_fixed(filename)
        content: str = self.load_content(filename)
        self.__parse_file_content(content)
        quest_filters = self.remote.data.quest_filters
        self.__remove_empty_and_other_language_and_filtered(language, quest_filters)
        self.__create_requirements_pointers()
        self.__create_cross_references()
        return self

    def load_content(self, filename: Path) -> str:
        content: str = ""
        if not filename.exists():
            if not self.remote.is_sandbox:
                if self.verbose:
                    logger.warning(t(_GAME_BUILDER_SOURCE_NOT_FOUND, filename=filename, name=self.remote.data.name))
        else:
            content = Decoder.load(filename)
        return content

    def __ensure_sandbox_readme_fixed(self, filename: Path):
        if not self.remote.is_sandbox:
            return
        if not filename.parent.exists():
            return
        if not filename.exists():
            # print(f"Aviso: fonte {filename} não encontrada no source {self.source.name}, criando arquivo")
            if self.verbose:
                logger.warning(t(_GAME_BUILDER_SOURCE_NOT_FOUND_CREATING, filename=filename, name=self.remote.data.name))
            filename.parent.mkdir(parents=True, exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# {self.remote.data.name}\n\n")
        work_dir = self.remote.path.work_dir
        if not work_dir.exists():
            return
        fix_readme(filename.resolve(), self.remote.path.work_dir, self.remote.data.name, verbose=False, load_titles=True)

    def collect_tasks(self) -> dict[str, Task]:
        tasks: dict[str, Task] = {}

        for quest in self.quests.values():
            for task in quest.get_tasks():
                tasks[task.basic.full_key] = task
        return tasks

    def collect_quests(self) -> dict[str, Quest]:
        quests: dict[str, Quest] = {}
        for quest in self.quests.values():
            quests[quest.basic.full_key] = quest
        return quests

    def __create_requirements_pointers(self):
        quests = self.remote.data.quest_filters
        if quests is not None:
            return

        filename: Path = self.remote.path.index_file
        quests = self.collect_quests()
        # verificar se todas as quests requeridas existem e adicionar o ponteiro
        for q in quests.values():
            for r in q.requirements.requires:
                if r in quests:
                    q.requirements.requires_ptr.append(quests[r])
                    quests[r].requirements.required_by_ptr.append(q)
                else:
                    if self.verbose:
                        logger.warning(
                            t(
                                _GAME_BUILDER_QUEST_REQUIRES_MISSING,
                                filename=filename,
                                line=q.source.line_number,
                                quest=str(q),
                                required=r,
                            )
                        )
                    exit(1)

    def __parse_file_content(self, content: str):
        lines = content.splitlines()
        alias = self.remote.data.name
        editable_source: bool = self.remote.data.is_editable
        source_dir_root: Path | None = self.remote.path.source_dir
        if source_dir_root is None:
            if self.verbose:
                logger.warning(t(_GAME_BUILDER_SOURCE_NO_ORIGIN_DIR, name=alias))
            return
        git_url: str | None = self.remote.data.git_url

        try:
            filename = self.remote.path.index_file
        except ValueError:
            if self.verbose and not self.remote.is_sandbox:
                logger.exception(t(_GAME_BUILDER_INDEX_FETCH_ERROR, name=alias))
            return
        for line_num, line in enumerate(lines):
            quest_parser = QuestParser(alias)
            quest = quest_parser.parse_quest(filename, line, line_num + 1)
            if quest is not None:
                self.__add_quest(quest_parser.finish_quest())
                continue
            tp = TaskParser(index_path=filename, remote_name=alias, remote_dir_root=source_dir_root, remote_git_url=git_url, editable_source=editable_source)
            task = tp.parse_line(line, line_num + 1)
            if task is not None:
                self.__add_task(task)

    def __get_active_quest(self) -> Quest:
        if self.active_quest is None:
            qkey = "_sem_quest"
            return self.__add_quest(Quest(t(_GAME_BUILDER_NO_QUEST_TITLE), qkey))
        return self.active_quest

    def __add_quest(self, quest: Quest) -> Quest:
        if quest.basic.full_key not in self.quests:
            # print("debug", f"Adding quest {quest.identity.full_key} with title {quest.identity.get_title()}")
            self.quests[quest.basic.full_key] = quest
        if quest.basic.full_key not in self.ordered_quests:
            self.ordered_quests.append(quest.basic.full_key)
        self.active_quest = quest
        return quest

    def __add_task(self, task: Task):
        self.__get_active_quest().add_task(task)

    def add_filtered_quests(self, quest_filters: dict[str, str] | None):
        if self.remote.is_sandbox:
            return
        if quest_filters is None or len(quest_filters) == 0:
            return
        quests: list[Quest] = []
        available_quests = [q for q in self.quests.values()]
        for pattern, destiny in quest_filters.items():
            for q in available_quests:
                if (pattern.lower() in q.basic.title.lower()) or (pattern.lower() == f"@{q.basic.key}".lower()):
                    if q.config.active is False:
                        continue
                    if destiny == "":
                        quests.append(q)
                    else:
                        qdestiny = self.quests.get(f"{self.remote.data.name}@{destiny}", None)
                        if qdestiny is None:
                            qdestiny = Quest(destiny, destiny)
                            qdestiny.basic.remote_name = self.remote.data.name
                            self.__add_quest(qdestiny)
                        for t in q.get_tasks():
                            qdestiny.add_task(t)
                        if qdestiny not in quests:
                            quests.append(qdestiny)
        self.quests = {q.basic.full_key: q for q in quests}

    def filter_by_language_and_empty(self, language: str):
        quests: list[Quest] = []
        for q in self.quests.values():
            if q.config.active is False:
                continue
            if len(q.get_tasks()) == 0:
                continue
            if len(q.config.languages) == 0 or language in q.config.languages:
                quests.append(q)
        self.quests = {q.basic.full_key: q for q in quests}
        return self

    def __remove_empty_and_other_language_and_filtered(self, language: str, quest_filters: dict[str, str] | None):
        if quest_filters is None or len(quest_filters) == 0:
            self.filter_by_language_and_empty(language)
        else:
            self.add_filtered_quests(quest_filters)
        return self

    def __create_cross_references(self):  # call after clear_empty
        for quest in self.quests.values():
            quest.basic.remote_name = self.remote.data.name
            for task in quest.get_tasks():
                task.basic.remote_name = self.remote.data.name
                task.quest_key = quest.basic.full_key
