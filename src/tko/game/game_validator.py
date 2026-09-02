from loguru import logger

from tko.game.quest import Quest
from tko.game.task import Task
from tko.i18n import Msg




_GAME_VALIDATOR_IGNORING_DUPLICATE_TASK = Msg.text(
    pt="Ignorando tarefa com chave repetida: {task_key}, arquivo={filename}, linha={line_number}, conteúdo={line}",
    en="Ignoring task with duplicate key: {task_key}, file={filename}, line={line_number}, content={line}",
)
_GAME_VALIDATOR_SELF_REF_ERROR = Msg.text(
    pt="Erro: auto referência {line_number} {line}",
    en="Error: self reference {line_number} {line}",
)
_GAME_VALIDATOR_CYCLE_DETECTED = Msg.text(
    pt="Cycle detected: {visited}",
    en="Cycle detected: {visited}",
)

class GameValidator:
    def __init__(self, quests: dict[str, Quest]):
        self.quests: dict[str, Quest] = quests
        self.tasks: dict[str, Task] = {}
        
    def validate(self):
        self.tasks.clear()
        self.__validate_requirements()
        self.__check_cycle()
        return self

    def __validate_requirements(self):
        # verify is there are keys repeated between quests, tasks and groups
        keys = set(self.quests.keys())
        for q in self.quests.values():
            accepted_tasks: list[Task] = []
            for task in q.get_tasks():
                if task.basic.full_key in keys:
                    logger.warning(
                        _GAME_VALIDATOR_IGNORING_DUPLICATE_TASK.t().format(
                            task_key=task.basic.full_key,
                            filename=task.location.index_path,
                            line_number=task.location.line_number,
                            line=task.location.line_data,
                        )
                    )
                    continue
                keys.add(task.basic.full_key)
                self.tasks[task.basic.full_key] = task
                accepted_tasks.append(task)
            q.set_tasks(accepted_tasks)

        # trim titles
        for q in self.quests.values():
            q.basic.title = q.basic.title.strip()

        # verificar auto dependencia
        for q in self.quests.values():
            for r in q.requirements.requires:
                if q.basic.full_key == r:
                    logger.error(str(_GAME_VALIDATOR_SELF_REF_ERROR).format(line_number=q.source.line_number, line=q.source.line))
                    exit(1)


    # call after create_requirements_pointers
    def __check_cycle(self):
        def dfs(qx: Quest, visitedx: list[str]):
            if len(visitedx) > 0:
                if visitedx[0] == qx.basic.full_key:
                    logger.error(str(_GAME_VALIDATOR_CYCLE_DETECTED).format(visited=visitedx))
                    exit(1)
            if qx.basic.full_key in visitedx:
                return
            visitedx.append(qx.basic.full_key)
            for r in qx.requirements.requires_ptr:
                dfs(r, visitedx)

        for q in self.quests.values():
            visited: list[str] = []
            dfs(q, visited)
