from __future__ import annotations
import sys # type: ignore
import logging
from tko.collect.task_game_data import TaskGameData
from tko.repository.repository import Repository
from tko.logger.logger import Logger
from tko.collect.task_user_data import TaskUserData
from tko.logger.log_sort import LogSort
from tko.play.daily_graph import DailyGraph
from tko.collect.quest_game_data import QuestGameData
from tko.i18n import Msg



logger = logging.getLogger(__name__)

CMD_COLLECT_REPO_NOT_FOUND = Msg(
    pt="Repositório não encontrado em {path}",
    en="Repository not found in {path}",
)
CMD_COLLECT_TKO_REPO_NOT_FOUND = Msg(
    pt="Repositório TKO não encontrado em {path}",
    en="TKO repo not found in {path}",
)
CMD_COLLECT_MULTIPLE_REPOS_FOUND = Msg(
    pt=" - Múltiplos repositórios TKO encontrados, usando o primeiro.",
    en=" - Multiple TKO repos found, using the first one.",
)
CMD_COLLECT_RUNNING_IN = Msg(
    pt="Executando tko collect em {folder}",
    en="Running tko collect in {folder}",
)
CMD_COLLECT_JSON_PARSE_FAILED = Msg(
    pt="Erro: Falha ao analisar saída JSON para {username}",
    en="Error: Failed to parse JSON output for {username}",
)
CMD_COLLECT_ERROR = Msg(
    pt="Erro: {error}",
    en="Error: {error}",
)
CMD_COLLECT_SAVING_EXTRACTED_DATA = Msg(
    pt="Salvando dados extraídos em {path}",
    en="Saving extracted data to {path}",
)

class CollectActions:
    @staticmethod
    def resume(repo: Repository) -> dict[str, TaskUserData]:
        """
        Collect resume data from the repository's logger and return a dictionary mapping task keys to TaskResume objects.
        """
        logger: Logger = repo.logger
        tasks: dict[str, LogSort] = logger.tasks.task_dict
        resume_dict: dict[str, TaskUserData] = {}

        game = repo.game
        quest_map: dict[str, str] = {}
        for quest in game.quests.values():
            for task in quest.get_tasks():
                quest_map[task.basic.full_key] = quest.basic.full_key
        for key, log_sort in tasks.items():
            quest_key = quest_map.get(key, "")
            resume = TaskUserData(key, quest_key).from_log_sort(log_sort)
            resume_dict[key] = resume
        return resume_dict

    @staticmethod
    def daily_graph(rep: Repository, width: int, height: int, colored: bool) -> str:
        dg = DailyGraph(rep.logger, width, height)
        header, image = dg.get_graph()
        if not colored:
            return "\n".join([x.get_str() for x in header + image])
        return "\n".join([str(x) for x in image])

    @staticmethod
    def load_game_as_quest_list(rep: Repository) -> list[QuestGameData]:
        game = rep.game
        if not game:
            return []
        output: list[QuestGameData] = []

        for quest in game.quests.values():
            output_quest = QuestGameData(quest.basic.full_key)
            output.append(output_quest)
            for task in quest.get_tasks():
                output_quest.tasks.append(TaskGameData(key=task.basic.full_key, value=task.game.xp, is_leet=task.config.is_auto))
        return output
    
