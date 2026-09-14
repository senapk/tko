from loguru import logger
from dataclasses import replace
from urllib.parse import urljoin
import re
from tko.game.game_builder import GameBuilder
from tko.game.game_validator import GameValidator
from tko.game.quest import Quest
from tko.game.task import Task
from tko.repository.remote import Source
from tko.i18n import Msg
from tko.repository.remote_resolver import SourceResolver
from tko.util.git_hub_url import GitHubUrl


_GAME_TASK_NOT_FOUND_IN_COURSE = Msg.text(
    pt="fail: tarefa '{task_key}' não encontrada no curso",
    en="fail: task '{task_key}' not found in course",
)
_GAME_SANDBOX_SOURCE_NOT_FOUND = Msg.text(
    pt="Local sandbox source not found",
    en="Local sandbox source not found",
)
_GAME_BUILD_FAILED_FOR_SOURCE = Msg.text(
    pt="Falha ao construir jogo para a fonte {name}",
    en="Failed to build game for source {name}",
)

def load_html_tags(task: str) -> None | str:
    pattern = r"<!--\s*(.*?)\s*-->"
    match = re.search(pattern, task)
    if not match:
        return None
    return match.group(1).strip()

class Game:
    def __init__(self):
        self.sources: dict[str, Source] = {}
        self.ordered_quests: list[str] = [] # ordered clusters
        self.quests: dict[str, Quest] = {}  # quests indexed by quest key
        self.tasks: dict[str, Task] = {}  # tasks indexed by task key
        self.language: str = ""

    def get_task_throw(self, key: str) -> Task:
        if key in self.tasks:
            return self.tasks[key]
        raise Warning(str(_GAME_TASK_NOT_FOUND_IN_COURSE).format(task_key=key))

    def get_task(self, key: str) -> Task | None:
        return self.tasks.get(key)
        
    def set_sources(self, sources: dict[str, Source], language: str):
        self.sources = sources
        self.language = language
        return self
    
    def build(self, source_resolver: SourceResolver) -> "Game":
        self.ordered_quests = []
        self.quests = {}
        self.tasks = {}
        for source in self.sources.values():
            index_file, ok = source_resolver.resolve_index_file(source, load_git=True)
            if not ok:
                logger.warning(str(_GAME_BUILD_FAILED_FOR_SOURCE).format(name=source.name))
                continue
            gb = GameBuilder(index_file, source.name, external_source=not source.is_editable)
            try:
                gb.build_from(self.language)
            except ValueError as exc:
                logger.exception("{}: {}", str(_GAME_BUILD_FAILED_FOR_SOURCE).format(name=source.name), exc)
                continue
            if source.is_git_source:
                # The index snapshot lives in the workspace, but relative task
                # links still name files in the original remote repository.
                for task in gb.collect_tasks().values():
                    if task.location.git_hub_url is None:
                        origin_url: str = urljoin(source.path_or_url, task.location.raw_link)
                        task.location = replace(
                            task.location, git_hub_url=GitHubUrl.parse(origin_url)
                        )
            for quest_key in gb.ordered_quests:
                self.ordered_quests.append(source.name + "@" + quest_key)
            gb_quests = gb.collect_quests()
            for quest in gb_quests.values():
                self.quests[quest.basic.full_key] = quest
        validator = GameValidator(self.quests).validate()
        self.tasks = validator.tasks
        return self
    

    # @override
    def __str__(self):
        output: list[str] = []
        for q in self.quests.values():
            output.append("  - " + str(q))
            for t in q.get_tasks():
                output.append("    - " + str(t))
        output.append(100 * "-")
        for q in self.quests.values():
            output.append(str(q))
        output.append(100 * "-")
        for t in self.tasks.values():
            output.append(str(t))
        return "\n".join(output)
