from __future__ import annotations

from tko.game.task_game import TaskGame
from tko.game.task_grader import TaskGrader
from tko.game.tree_item import TreeBasic, TreeUi
from tko.game.task_info import TaskSelfInfo
from tko.game.task_config import TaskConfig
from tko.game.task_location import TaskLocation

class Task:
    """
    Representa uma tarefa (atividade) do sistema TKO.

    Campos principais:
        - basic: informações básicas (chave, título, etc)
        - config: configuração da tarefa (tipo, teste, penalidade)
        - resource: informações do recurso (link, tipo, linha de origem)
        - game: informações de gamificação (xp, skills)

    O título da tarefa normalmente é carregado do índice (texto entre colchetes na linha do índice).
    """
    def __init__(self):
        self.quest_key: str = ""
        self.basic: TreeBasic = TreeBasic()
        self.ui: TreeUi = TreeUi()
        self.info: TaskSelfInfo = TaskSelfInfo()
        self.config: TaskConfig = TaskConfig()
        self.location: TaskLocation = TaskLocation()
        self.game: TaskGame = TaskGame()
        
        self.main_idx = 0

    @property
    def grader(self) -> TaskGrader:
        return TaskGrader(self.info)
    def clone(self) -> Task:
        new_task = Task()
        new_task.quest_key = self.quest_key
        new_task.basic = self.basic.clone()
        new_task.ui = self.ui.clone()
        new_task.info = self.info.clone()
        new_task.config = self.config.clone()
        new_task.location = self.location.clone()
        new_task.game = self.game.clone()
        return new_task
    
    def is_db_empty(self) -> bool:
        return len(self.info.get_kv()) == 0

    # @override
    def __str__(self):
        lnum = str(self.location.line_number).rjust(3)
        key = "" if self.basic.full_key == self.basic.title else self.basic.full_key + " "
        return f"{lnum} key:{key} title:{self.basic.title} skills:{self.game.skill} remote:{self.location.raw_link}"
