from tko.game.cluster import Cluster
from tko.game.quest import Quest
from tko.game.task import Task

class GameValidator:
    def __init__(self, clusters: dict[str, Cluster]):
        self.clusters: dict[str, Cluster] = clusters
        self.quests: dict[str, Quest] = {}
        self.tasks: dict[str, Task] = {}
        
    def validate(self):
        self.__validate_requirements()
        self.__check_cycle()
        return self

    def __validate_requirements(self):
        # verify is there are keys repeated between quests, tasks and groups
        keys = [c.get_db_key() for c in self.clusters.values()] +\
               [k for k in self.quests.keys()] +\
               [k for k in self.tasks.keys()]

        # print chaves repetidas
        for k in keys:
            if keys.count(k) > 1:
                print(f"Chave repetida: {k}")
                exit(1)

        # trim titles
        for q in self.quests.values():
            q.set_title(q.get_title().strip())
        for c in self.clusters.values():
            c.set_title(c.get_title().strip())

        # verificar auto dependencia
        for q in self.quests.values():
            for r in q.requires:
                if q.get_db_key() == r:
                    print(f"Erro: auto refência {q.line_number} {q.line}")
                    exit(1)


    # call after create_requirements_pointers
    def __check_cycle(self):
        def dfs(qx: Quest, visitedx: list[str]):
            if len(visitedx) > 0:
                if visitedx[0] == qx.get_db_key():
                    print(f"Cycle detected: {visitedx}")
                    exit(1)
            if q.get_db_key() in visitedx:
                return
            visitedx.append(q.get_db_key())
            for r in q.requires_ptr:
                dfs(r, visitedx)

        for q in self.quests.values():
            visited: list[str] = []
            dfs(q, visited)