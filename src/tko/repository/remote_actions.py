import logging
from tko.repository.remote import Remote
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.repository.repository_loader import RepositoryLoader
from tko.util.rtext import RText
from tko.i18n import MsgKey, t
from pathlib import Path


logger = logging.getLogger(__name__)

class RemoteActions:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo

    def remote_list(self):
        remotes = self.repo.remotes
        print(t(MsgKey.REMOTE_EDIT_HINT))
        print(RText.parse(f"[y]{self.repo.paths.config_file}[.]"))
        if len(remotes) == 0:
            print(t(MsgKey.REMOTE_NONE_CONFIGURED))
            return
        print(t(MsgKey.REMOTE_CONFIGURED_SOURCES))
        for remote in remotes:
            self.show_source(remote)
    
    def show_source(self, remote: Remote):
        print(RText.parse(f"[y]{t(MsgKey.REMOTE_LABEL)} {remote.data.name}[.]"))
        print(RText.parse(f"  [y]{t(MsgKey.REMOTE_LINK)} {remote.data.target}[.]"))
        print(RText.parse(f"  [y]{t(MsgKey.REMOTE_INDEX)} {remote.data.index}[.]"))
        status = t(MsgKey.REMOTE_FILTER_DISABLED) if remote.data.quest_filters is None else t(MsgKey.REMOTE_FILTER_ENABLED)
        print(RText.parse(f"  [y]{t(MsgKey.REMOTE_QUEST_FILTER)} {status}[.]"))
        if remote.data.quest_filters is not None:
            for f, v in remote.data.quest_filters.items():
                print(f"    - {f}: {v}")

    def remote_rm(self, alias: str) -> None:
        found = False
        for remote in self.repo.remotes:
            if remote.data.name == alias:
                found = True
                self.repo.data.del_remote(alias)
                print(RText.parse(f"[y]{t(MsgKey.REMOTE_REMOVED_SUCCESS, alias=alias)}[.]"))
                break
        if not found:
            raise Warning(t(MsgKey.REMOTE_NOT_FOUND))
        RepositoryLoader(self.repo).save_config()

    def remote_set(self, alias: str, target: str | None = None, index: str | None = None) -> None:
        repo = self.repo
        remote: Remote | None = repo.data.get_remote(alias)
        if remote is None:
            raise Warning(t(MsgKey.REMOTE_NOT_FOUND))
        change: bool = False

        if target is not None:
            remote.data.target = target
            change = True
        if index is not None:
            remote.data.index = index
            change = True
        self.show_source(remote)
        if change:
            print(RText.parse(f"[y]{t(MsgKey.REMOTE_FILTERS_UPDATED, alias=alias)}[.]"))
            RepositoryLoader(repo).save_config()

    def remote_filter(self, alias: str, filter_quest: list[str] | None = None, clear: bool = False, filter_to: str | None = None) -> None:
        repo = self.repo
        source = repo.data.get_remote(alias)
        if source is None:
            raise Warning(t(MsgKey.REMOTE_NOT_FOUND))
        change: bool = False

        if filter_quest is not None:
            if source.data.quest_filters is None:
                source.data.quest_filters = {}
            for f in filter_quest:
                if f not in source.data.quest_filters:
                    change = True
                    source.data.quest_filters[f] = filter_to if filter_to is not None else ""
            
        if clear:
            change = True
            source.data.quest_filters = None
        
        # if not quests and not tasks and not clear:
        self.show_source(source)
        if change:
            print(RText.parse(f"[y]{t(MsgKey.REMOTE_FILTERS_UPDATED, alias=alias)}[.]"))
            RepositoryLoader(repo).save_config()

    def fix_filter(self, source: list[str] | None, destiny: str | None) -> dict[str, str] | None:
        if source is None:
            return None
        return {s: destiny if destiny is not None else "" for s in source}

    def remote_add(
            self, 
            name: str, 
            remote_default: str | None, 
            remote_url: str | None, 
            remote_dir: str | None, 
            index: str | None,
            filter_quest: list[str] | None, 
            filter_task: list[str] | None, 
            filter_to: str | None,
            writeable: bool, branch: str = "main"
            ) -> None:
        
        remotes = self.repo.remotes
        if any(remote.data.name == name for remote in remotes):
            raise Warning(t(MsgKey.REMOTE_NAME_EXISTS))

        repo = self.repo
        if remote_default is not None:
            print(RText.parse(f"[y]{t(MsgKey.REMOTE_ADDING_GIT, url=remote_default)}[.]"))
            url: str = ""
            settings = self.settings
            if not settings.has_alias_git(remote_default):
                raise Warning(t(MsgKey.REMOTE_GIT_ALIAS_NOT_FOUND))
            try:
                url = settings.get_alias_git(remote_default)
                self.git_clone_repository(url)
                remote = Remote(alias=name)
                remote.data.set_git_source(target=url, branch=branch, index=index)
                remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
                self.repo.data.set_remote(remote)
            except Warning:
                logger.exception(t(MsgKey.REMOTE_CLONE_ERROR))
                raise Warning(t(MsgKey.REMOTE_CLONE_FAILED))
        elif remote_dir is not None:
            dir_path = Path(remote_dir)
            if not dir_path.exists() or not dir_path.is_dir():
                raise Warning(t(MsgKey.REMOTE_DIR_NOT_FOUND))
            print(RText.parse(f"[y]{t(MsgKey.REMOTE_ADDING_LOCAL, path=dir_path)}[.]"))
            remote = Remote(alias=name)
            remote.data.set_local_source(target=dir_path)
            remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
            self.repo.data.set_remote(remote)
        elif remote_url is not None:
            print(RText.parse(f"[y]{t(MsgKey.REMOTE_ADDING_URL, url=remote_url)}[.]"))
            try:
                self.git_clone_repository(remote_url)
                remote = Remote(alias=name)
                remote.data.set_git_source(target=remote_url, branch=branch, index=index)
                remote.data.quest_filters = self.fix_filter(filter_quest, filter_to)
                remote.data.is_editable = writeable
                self.repo.data.set_remote(remote)
                print(RText.parse(f"[y]{t(MsgKey.REMOTE_ADDED_SUCCESS, name=name)}[.]"))
            except Warning:
                logger.exception(t(MsgKey.REMOTE_CLONE_ERROR))
                raise Warning(t(MsgKey.REMOTE_CLONE_FAILED))
        RepositoryLoader(repo).save_config()
   
    def git_clone_repository(self, link: str) -> None:
        print(RText.parse(f"[y]{t(MsgKey.REMOTE_CLONING, link=link)}[.]"))
        repo_dir = self.repo.git_cache.get_remote_dir(link, verbose=True)
        if repo_dir is None:
            raise Warning(t(MsgKey.REMOTE_CLONE_FAILED))
        print(RText.parse(f"[y]{t(MsgKey.REMOTE_CLONED_SUCCESS, link=link)}[.]\n"))
        


    def print_end_msg(self):
        print(RText.parse(f"[y]{t(MsgKey.REMOTE_CAN_ACCESS)}[.]\n"))
        
