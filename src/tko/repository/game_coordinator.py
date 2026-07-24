from __future__ import annotations
from loguru import logger
from tko.i18n import Msg
from tko.game.task import Task
from tko.logger.log_sort import LogSort
from tko.repository.repository import Repository
from tko.repository.remote_resolver import RemoteResolver
from tko.feno.indexer import fix_readme

from tko.repository.sandbox import Sandbox

_GAME_COORDINATOR_LOADING_REPOSITORY = Msg.text(
    pt="Carregando repositório de {root}...",
    en="Loading repository from {root}...",
)

class GameCoordinator:

    def __init__(self, repo: Repository): 
        self.repo = repo

    def load_game(self) -> GameCoordinator:
        logger.debug(str(_GAME_COORDINATOR_LOADING_REPOSITORY).format(root=self.repo.paths.root_dir))
        rr = RemoteResolver(self.repo.git_cache, self.repo.paths.root_dir)
        
        remotes = self.repo.remotes
        if not remotes: # load now
            from tko.repository.repository_config import RepositoryLoader
            RepositoryLoader(self.repo).load()
            remotes = self.repo.remotes
        self.ensure_sandbox_readme_fixed(self.repo, rr)
        self.repo.game.set_remotes(remotes, self.repo.data.lang)
        self.repo.game.build(remote_resolver = rr)
        self._load_tasks_from_log_into_game()
        return self
    


    def _load_tasks_from_log_into_game(self):
        task_dict: dict[str, LogSort] = self.repo.logger.tasks.task_dict
        for key, task_log in task_dict.items():
            if key not in self.repo.game.tasks:
                continue
            task: Task = self.repo.game.tasks[key]
            
            self_list = task_log.self_list
            if self_list:
                _, self_item = self_list[-1]
                task.info.copy_quality_from(self_item.info)

            if task.config.is_eval_self:
                if self_list:
                    _, self_item = self_list[-1]
                    task.info.rate = self_item.info.rate
            else:
                exec_list = task_log.exec_list
                if exec_list:
                    _, exec_item = exec_list[-1]
                    task.info.rate = exec_item.rate


    def ensure_sandbox_readme_fixed(self, repo: Repository, remote_resolver: RemoteResolver):
        basedir = repo.data.sandbox_dir
        filename = repo.data.sandbox_index_file
        if not filename.parent.exists():
            return
        if basedir.exists() and not filename.exists():
            filename.parent.mkdir(parents=True, exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# {Sandbox.get_sandbox_name()}\n\n")
        fix_readme(filename.resolve(), basedir, Sandbox.get_sandbox_name(), verbose=False, load_titles=True)
