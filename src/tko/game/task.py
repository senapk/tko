from __future__ import annotations

from tko.game.task_game import TaskGame
from tko.game.task_grader import TaskGrader
from tko.game.tree_item import TreeItem
from tko.game.task_info import TaskSelfInfo
from tko.game.task_config import TaskConfig
from tko.game.task_location import TaskLocation
from tko.game.task_enums import TaskType

class Task(TreeItem):
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
        super().__init__()
        self.info: TaskSelfInfo = TaskSelfInfo()
        self.config: TaskConfig = TaskConfig()
        self.location: TaskLocation = TaskLocation()
        self.game: TaskGame = TaskGame()
        self.is_reference: bool = False
        self.quest_key: str = ""
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
        new_task.is_reference = self.is_reference
        return new_task

    @property
    def xp(self) -> float:
        """Gamification value of the task based on its configured attributes."""
        if self.config.type == TaskType.WIKI:
            return 0.0
        return (self.game.gain * self.game.hard * self.game.size) / 4
    
    def is_db_empty(self) -> bool:
        return len(self.info.get_kv()) == 0

    # @override
    def __str__(self):
        lnum = str(self.location.line_number).rjust(3)
        key = "" if self.basic.full_key == self.basic.title else self.basic.full_key + " "
        return f"{lnum} key:{key} title:{self.basic.title} skills:{self.game.skill} source:{self.location.raw_link}"
