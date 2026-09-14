from pathlib import Path
from loguru import logger

from tko.game.quest_parser import QuestParser
from tko.game.task_parser import TaskParser
from tko.game.quest import Quest
from tko.game.task import Task
from tko.util.decoder import Decoder
from tko.i18n import Msg
from tko.game.source_xp_config import SourceXpConfig

_GAME_BUILDER_README_FETCH_ERROR = Msg.text(
    pt="Erro ao obter o arquivo README da fonte {name}",
    en="Error fetching README file from source {name}",
)
_GAME_BUILDER_SOURCE_NOT_FOUND = Msg.text(
    pt="Aviso: fonte {filename} não encontrada no source {name}",
    en="Warning: source {filename} not found in source {name}",
)
_GAME_BUILDER_SOURCE_NOT_FOUND_CREATING = Msg.text(
    pt="Aviso: fonte {filename} não encontrada no source {name}, criando arquivo",
    en="Warning: source {filename} not found in source {name}, creating file",
)
_GAME_BUILDER_DUPLICATE_QUEST = Msg.text(
    pt="Ignorando quest com chave repetida: {key}, arquivo={filename}, linha={line_number}, conteúdo={line}",
    en="Ignoring quest with duplicate key: {key}, file={filename}, line={line_number}, content={line}",
)
_GAME_BUILDER_DUPLICATE_TASK = Msg.text(
    pt="Ignorando tarefa com chave repetida: {key}, arquivo={filename}, linha={line_number}, conteúdo={line}",
    en="Ignoring task with duplicate key: {key}, file={filename}, line={line_number}, content={line}",
)
_GAME_BUILDER_NO_QUEST_TITLE = Msg.text(
    pt="Sem Quest",
    en="No Quest",
)


class GameBuilder:
    def __init__(self, index_path: Path, source_name: str, external_source: bool = False):
        self.index_path = index_path
        self.source_name = source_name
        self.external_source = external_source

        self.ordered_quests: list[str] = []  # ordered quests keys
        self.quests: dict[str, Quest] = {}
        self.active_quest: Quest | None = None
        self._registered_keys: set[str] = set()
        self.interactive: bool = False
        self.xp_config = SourceXpConfig(source_name=source_name, index_path=index_path)

    def set_interactive(self, interactive: bool):
        self.interactive = interactive
        return self

    def build_from(self, language: str) -> bool:
        self.ordered_quests = []
        self.quests = {}
        self.active_quest = None
        self._registered_keys.clear()

        filename = self.index_path
        content = Decoder.load(filename)
        self.xp_config = SourceXpConfig.from_markdown(content, self.source_name, filename)
        self.__parse_file_content(content)
        self.__remove_empty_and_other_language_and_filtered(language)
        self.__calculate_total_xp()
        self.__create_cross_references()
        return True



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

    def __sum_quest_xp(self, quest: Quest) -> float:
        tasks = quest.get_tasks()
        references = [task for task in tasks if task.is_reference]
        if references:
            tasks = references
        return sum(task.xp for task in tasks)

    def __calculate_total_xp(self):
        for quest in self.quests.values():
            if quest.game.goal_xp == 0:
                quest.game.goal_xp = self.__sum_quest_xp(quest)

    def __parse_file_content(self, content: str):
        lines = content.splitlines()
        for line_num, line in enumerate(lines):
            quest_parser = QuestParser(self.source_name)
            quest = quest_parser.parse_quest(self.index_path, line, line_num + 1)
            if quest is not None:
                self.__add_quest(quest_parser.finish_quest())
                continue
            tp = TaskParser(
                index_path=self.index_path,
                external_source=self.external_source,
                xp_config=self.xp_config,
            )
            task = tp.parse_line(line, line_num + 1)
            if task is not None:
                task.basic.source_name = self.source_name
                self.__add_task(task)

    def __get_active_quest(self) -> Quest:
        if self.active_quest is None:
            qkey = "_sem_quest"
            return self.__add_quest(Quest(str(_GAME_BUILDER_NO_QUEST_TITLE), qkey))
        return self.active_quest

    def __add_quest(self, quest: Quest) -> Quest:
        key = quest.basic.key
        if key in self._registered_keys:
            logger.warning(
                _GAME_BUILDER_DUPLICATE_QUEST.t().format(
                    key=key,
                    filename=self.index_path,
                    line_number=quest.source.line_number,
                    line=quest.source.line,
                )
            )
            if self.active_quest is None:
                raise ValueError(f"Duplicate quest key without an active quest: {key}")
            return self.active_quest

        self._registered_keys.add(key)
        self.quests[quest.basic.full_key] = quest
        self.ordered_quests.append(quest.basic.full_key)
        self.active_quest = quest
        return quest

    def __add_task(self, task: Task):
        active_quest = self.__get_active_quest()
        key = task.basic.key
        if key in self._registered_keys:
            logger.warning(
                _GAME_BUILDER_DUPLICATE_TASK.t().format(
                    key=key,
                    filename=self.index_path,
                    line_number=task.location.line_number,
                    line=task.location.line_data,
                )
            )
            return
        self._registered_keys.add(key)
        active_quest.add_task(task)

    def filter_by_language_and_empty(self, language: str):
        quests: list[Quest] = []
        for q in self.quests.values():
            if q.game.active is False:
                continue
            if len(q.get_tasks()) == 0:
                continue
            if len(q.game.languages) == 0 or language in q.game.languages:
                quests.append(q)
        self.quests = {q.basic.full_key: q for q in quests}
        return self

    def __remove_empty_and_other_language_and_filtered(self, language: str):
        self.filter_by_language_and_empty(language)
        return self

    def __create_cross_references(self):  # call after clear_empty
        for quest in self.quests.values():
            quest.basic.source_name = self.source_name
            for task in quest.get_tasks():
                task.basic.source_name = self.source_name
                task.quest_key = quest.basic.full_key
