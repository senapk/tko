from __future__ import annotations
from loguru import logger
from tko.i18n import Msg
from tko.game.task import Task
from tko.logger.log_sort import LogSort
from tko.repository.repository import Repository
from tko.repository.remote_resolver import SourceResolver
from tko.feno.indexer import fix_readme

_GAME_COORDINATOR_LOADING_REPOSITORY = Msg.text(
    pt="Carregando repositório de {root}...",
    en="Loading repository from {root}...",
)

class GameCoordinator:

    def __init__(self, repo: Repository): 
        self.repo = repo

    def load_game(self) -> GameCoordinator:
        logger.debug(str(_GAME_COORDINATOR_LOADING_REPOSITORY).format(root=self.repo.paths.root_dir))
        resolver = SourceResolver(self.repo.git_cache, self.repo.paths.root_dir)
        
        sources = self.repo.sources
        if not sources: # load now
            from tko.repository.repository_config import RepositoryLoader
            RepositoryLoader(self.repo).load()
            sources = self.repo.sources
        self.ensure_managed_readmes_fixed(self.repo, resolver)
        self.repo.game.set_sources(sources, self.repo.data.lang)
        self.repo.game.build(source_resolver=resolver)
        self._load_tasks_from_log_into_game()
        return self
    


    def _load_tasks_from_log_into_game(self):
        task_dict: dict[str, LogSort] = self.repo.logger.tasks.task_dict
        for key, task_log in task_dict.items():
            if key not in self.repo.game.tasks:
                continue
            task: Task = self.repo.game.tasks[key]
            if not task.config.awards_xp:
                continue
            
            self_list = task_log.self_list
            if self_list:
                _, self_item = self_list[-1]
                task.info.copy_quality_from(self_item.info)

            if not task.config.is_automated:
                if self_list:
                    _, self_item = self_list[-1]
                    task.info.rate = self_item.info.rate
            else:
                exec_list = task_log.exec_list
                if exec_list:
                    _, exec_item = exec_list[-1]
                    task.info.rate = exec_item.rate


    def ensure_managed_readmes_fixed(self, repo: Repository, resolver: SourceResolver):
        for source in repo.sources.values():
            if not resolver.is_local_internal(source):
                continue
            basedir = resolver.source_work_dir(source)
            filename = resolver.resolve_index_file(source, load_git=False)[0]

            if not filename.parent.exists():
                continue
            if basedir.exists() and not filename.exists():
                filename.parent.mkdir(parents=True, exist_ok=True)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"# {source.name}\n\n")
            if filename.exists():
                fix_readme(
                    index=filename.resolve(),
                    base_dir=basedir,
                    verbose=False,
                    load_titles=True,
                    yes=True,
                    warn_key_path_mismatches=True,
                )
