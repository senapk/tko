import logging

from tko.game.quest import Quest
from tko.game.task import Task


logger = logging.getLogger(__name__)

class GameValidator:
    def __init__(self, quests: dict[str, Quest]):
        self.quests: dict[str, Quest] = quests
        self.tasks: dict[str, Task] = {}
        
    def validate(self):
        self.__validate_requirements()
        self.__check_cycle()
        return self

    def __validate_requirements(self):
        # verify is there are keys repeated between quests, tasks and groups
        keys = [k for k in self.quests.keys()]
        for q in self.quests.values():
            for t in q.get_tasks():
                if t.basic.full_key in keys:
                    logger.error(
                        "Chave repetida: %s em %s %s, ignorando tarefa",
                        t.basic.full_key,
                        t.resource.line_number,
                        t.resource.line_data,
                    )
                    continue
                keys.append(t.basic.full_key)
                self.tasks[t.basic.full_key] = t

        # print chaves repetidas
        for k in keys:
            if keys.count(k) > 1:
                logger.error("Chave repetida: %s", k)
                exit(1)

        # trim titles
        for q in self.quests.values():
            q.basic.title = q.basic.title.strip()

        # verificar auto dependencia
        for q in self.quests.values():
            for r in q.requirements.requires:
                if q.basic.full_key == r:
                    logger.error("Erro: auto refência %s %s", q.source.line_number, q.source.line)
                    exit(1)


    # call after create_requirements_pointers
    def __check_cycle(self):
        def dfs(qx: Quest, visitedx: list[str]):
            if len(visitedx) > 0:
                if visitedx[0] == qx.basic.full_key:
                    logger.error("Cycle detected: %s", visitedx)
                    exit(1)
            if qx.basic.full_key in visitedx:
                return
            visitedx.append(qx.basic.full_key)
            for r in qx.requirements.requires_ptr:
                dfs(r, visitedx)

        for q in self.quests.values():
            visited: list[str] = []
            dfs(q, visited)