import sys
from tko.repository.git_cache import UpdateMode
from tko.repository.rep_source import RepSource
from tko.logger.log_sort import LogSort
from tko.repository.repository import Repository

class GameCoordinator:
    def __init__(self, repo: Repository): 
        self.repo = repo

    def load_game(self, verbose: bool) -> 'GameCoordinator':
        if verbose:
            print(f"Loading repository from {self.repo.paths.get_repo_root_dir()}...", file=sys.stderr)
            
        if not self.repo.data.get_sources():
            from tko.repository.repository_loader import RepositoryLoader
            RepositoryLoader(self.repo).load_config()
            
        if self.repo.git_cache.update_mode == UpdateMode.ALWAYS:
            for source in self.repo.data.get_sources():
                _ = source.get_source_readme(verbose)
                
        sources: list[RepSource] = self.repo.data.get_sources()
        self.repo.game.set_sources(sources, self.repo.data.lang)
        self.repo.game.build(verbose)
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
