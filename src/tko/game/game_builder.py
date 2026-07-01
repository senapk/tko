from pathlib import Path
from loguru import logger

from tko.game.quest_parser import QuestParser
from tko.game.task_parser import TaskParser
from tko.game.quest import Quest
from tko.game.task import Task
from tko.util.decoder import Decoder
from tko.i18n import Msg

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
_GAME_BUILDER_QUEST_REQUIRES_MISSING = Msg.text(
    pt="Quest\n{filename}:{line}\n{quest}\nrequer {required} que não existe",
    en="Quest\n{filename}:{line}\n{quest}\nrequires {required} that does not exist",
)
_GAME_BUILDER_NO_QUEST_TITLE = Msg.text(
    pt="Sem Quest",
    en="No Quest",
)


class GameBuilder:
    def __init__(self, index_path: Path, remote_name: str, remote_import: bool = False):
        self.index_path = index_path
        self.remote_name = remote_name
        self.remote_import = remote_import

        self.ordered_quests: list[str] = []  # ordered quests keys
        self.quests: dict[str, Quest] = {}
        self.active_quest: Quest | None = None
        self.interactive: bool = False

    def set_interactive(self, interactive: bool):
        self.interactive = interactive
        return self

    def build_from(self, language: str) -> bool:
        
        filename = self.index_path
        content = Decoder.load(filename)
        self.__parse_file_content(content)
        self.__remove_empty_and_other_language_and_filtered(language)
        self.__calculate_total_xp()
        self.__create_requirements_pointers()
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

    def __sum_quest_xp(self, quest: Quest):
        total = 0
        for t in quest.get_tasks():
            total += t.game.xp
        return total

    def __calculate_total_xp(self):
        for quest in self.quests.values():
            if quest.game.goal_xp == 0:
                quest.game.goal_xp = self.__sum_quest_xp(quest)


    def __create_requirements_pointers(self):
        filename: Path = self.index_path
        quests = self.collect_quests()
        # verificar se todas as quests requeridas existem e adicionar o ponteiro
        for q in quests.values():
            for r in q.requirements.requires:
                if r in quests:
                    q.requirements.requires_ptr.append(quests[r])
                    quests[r].requirements.required_by_ptr.append(q)
                else:
                    logger.warning(
                        _GAME_BUILDER_QUEST_REQUIRES_MISSING.t().format(filename=filename,
                            line=q.source.line_number,
                            quest=str(q),
                            required=r,
                        )
                    )
                    exit(1)

    def __parse_file_content(self, content: str):
        lines = content.splitlines()
        for line_num, line in enumerate(lines):
            quest_parser = QuestParser(self.remote_name)
            quest = quest_parser.parse_quest(self.index_path, line, line_num + 1)
            if quest is not None:
                self.__add_quest(quest_parser.finish_quest())
                continue
            tp = TaskParser(index_path=self.index_path, remote_import = self.remote_import)
            task = tp.parse_line(line, line_num + 1)
            if task is not None:
                task.basic.remote_name = self.remote_name
                self.__add_task(task)

    def __get_active_quest(self) -> Quest:
        if self.active_quest is None:
            qkey = "_sem_quest"
            return self.__add_quest(Quest(str(_GAME_BUILDER_NO_QUEST_TITLE), qkey))
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
            quest.basic.remote_name = self.remote_name
            for task in quest.get_tasks():
                task.basic.remote_name = self.remote_name
                task.quest_key = quest.basic.full_key
