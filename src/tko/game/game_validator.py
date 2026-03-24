from tko.game.quest import Quest
from tko.game.task import Task

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
                if t.get_full_key() in keys:
                    print(f"Chave repetida: {t.get_full_key()} em {t.line_number} {t.line}")
                    exit(1)
                keys.append(t.get_full_key())
                self.tasks[t.get_full_key()] = t

        # print chaves repetidas
        for k in keys:
            if keys.count(k) > 1:
                print(f"Chave repetida: {k}")
                exit(1)

        # trim titles
        for q in self.quests.values():
            q.set_title(q.get_title().strip())

        # verificar auto dependencia
        for q in self.quests.values():
            for r in q.requires:
                if q.get_full_key() == r:
                    print(f"Erro: auto refência {q.line_number} {q.line}")
                    exit(1)


    # call after create_requirements_pointers
    def __check_cycle(self):
        def dfs(qx: Quest, visitedx: list[str]):
            if len(visitedx) > 0:
                if visitedx[0] == qx.get_full_key():
                    print(f"Cycle detected: {visitedx}")
                    exit(1)
            if q.get_full_key() in visitedx:
                return
            visitedx.append(q.get_full_key())
            for r in q.requires_ptr:
                dfs(r, visitedx)

        for q in self.quests.values():
            visited: list[str] = []
            dfs(q, visited)