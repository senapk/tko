from __future__ import annotations
import sys
from tko.repository.git_cache import UpdateMode
from tko.logger.log_sort import LogSort
from tko.repository.repository import Repository

class GameCoordinator:
    def __init__(self, repo: Repository): 
        self.repo = repo

    def load_game(self, verbose: bool) -> GameCoordinator:
        if verbose:
            print(f"Loading repository from {self.repo.paths.root_dir}...", file=sys.stderr)
        
        remotes = self.repo.remotes
        if not remotes: # load now
            from tko.repository.repository_loader import RepositoryLoader
            RepositoryLoader(self.repo).load_config()
            remotes = self.repo.remotes
        else: # update cache if needed
            if self.repo.git_cache.update_mode == UpdateMode.ALWAYS:
                for remote in remotes:
                    _ = remote.path.index_file
                
        self.repo.game.set_remotes(remotes, self.repo.data.lang)
        self.repo.game.build(verbose, git_cache=self.repo.git_cache, root_dir=self.repo.root_dir)
        self._load_tasks_from_log_into_game()
        
        return self

    def _load_tasks_from_log_into_game(self):
        task_dict: dict[str, LogSort] = self.repo.logger.tasks.task_dict
        for key, task_log in task_dict.items():
            if key not in self.repo.game.tasks:
                continue
            task = self.repo.game.tasks[key]
            
            self_list = task_log.self_list
            if self_list:
                _, self_item = self_list[-1]
                task.info.copy_quality_from(self_item.info)

            exec_list = task_log.exec_list
            if exec_list:
                _, exec_item = exec_list[-1]
                task.info.rate = exec_item.rate
