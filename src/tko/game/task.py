from __future__ import annotations
from pathlib import Path

from tko.game.task_game import TaskGame
from tko.game.task_grader import TaskGrader
from tko.game.task_path import TaskPath
from tko.game.tree_item import TreeBasic, TreeUi
from tko.game.task_info import TaskSelfInfo
from tko.game.task_config import TaskConfig
from tko.game.task_resource import TaskResource
from tko.repository.git_cache import GitCache

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
        self.resource: TaskResource = TaskResource()
        self.game: TaskGame = TaskGame()
        
        self.main_idx = 0
        self.git_cache: GitCache | None = None
        self.root_dir: Path | None = None

    @property
    def path(self) -> TaskPath:
        if self.git_cache is None:
            raise ValueError(f"Git cache is not set for task resolver in {self.basic.full_key}")
        if self.root_dir is None:
            raise ValueError(f"Root directory is not set for task resolver in {self.basic.full_key}")
        return TaskPath(self.git_cache, self.root_dir, self.resource, self.basic)

    @property
    def grader(self) -> TaskGrader:
        return TaskGrader(self.config.loss, self.info)

    def clone(self) -> Task:
        new_task = Task()
        new_task.quest_key = self.quest_key
        new_task.basic = self.basic.clone()
        new_task.ui = self.ui.clone()
        new_task.info = self.info.clone()
        new_task.config = self.config.clone()
        new_task.resource = self.resource.clone()
        new_task.game = self.game.clone()
        new_task.git_cache = self.git_cache
        new_task.root_dir = self.root_dir
        return new_task
    
    def is_db_empty(self) -> bool:
        return len(self.info.get_kv()) == 0

    # @override
    def __str__(self):
        lnum = str(self.resource.line_number).rjust(3)
        key = "" if self.basic.full_key == self.basic.title else self.basic.full_key + " "
        return f"{lnum} key:{key} title:{self.basic.title} skills:{self.game.tags} remote:{self.resource.raw_link}"
