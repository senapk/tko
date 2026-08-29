from tko.util.git_hub_url import GitHubUrl
from tko.repository.git_cache import GitCache
from pathlib import Path

from tko.i18n import Msg
from tko.repository.remote import Remote, SourceType


_REMOTE_PATH_SOURCE_DIR_NOT_EXISTS = Msg.text(
    pt="Diretório de origem não existe",
    en="Source directory does not exist",
)
_REMOTE_PATH_INDEX_FILE_NOT_EXISTS = Msg.text(
    pt="Arquivo de índice não existe",
    en="Index file does not exist",
)

class RemoteResolver:
    def __init__(self, git_cache: GitCache, root_dir: Path):
        self.git_cache: GitCache = git_cache
        self.repo_root_dir: Path = root_dir.resolve()

    def remote_work_dir(self, remote: Remote) -> Path:
        return self.repo_root_dir / remote.name

    def is_local_internal(self, remote: Remote) -> bool:
        if remote.source_type != SourceType.LOCAL_FILE:
            return False
        path = self.resolve_local_uri(remote.path_or_url)
        return path.is_relative_to(self.repo_root_dir)

    def is_editable_index(self, remote: Remote) -> bool:
        if remote.source_type != SourceType.LOCAL_FILE:
            return False
        return self.is_local_internal(remote)

    def source_activity_dir(self, remote: Remote) -> Path:
        return self.remote_work_dir(remote)

    def resolve_local_uri(self, uri: str) -> Path:
        path = Path(uri)
        if path.is_absolute():
            return path.resolve()
        return (self.repo_root_dir / path).resolve()

    def serialize_uri(self, remote: Remote) -> str:
        if remote.source_type == SourceType.GIT_SOURCE:
            return remote.path_or_url
        path = self.resolve_local_uri(remote.path_or_url)
        if path.is_relative_to(self.repo_root_dir):
            return path.relative_to(self.repo_root_dir).as_posix()
        return path.as_posix()
    
    def resolve_index_file(self, remote: Remote, load_git: bool) -> tuple[Path , bool]:
        if remote.source_type == SourceType.GIT_SOURCE:
            ghu = GitHubUrl.parse(remote.path_or_url)
            if ghu is None or ghu.relative_path is None:
                return Path(), False
            folder, found = self.git_cache.get_repository_dir(ghu.repository_url, load_git=load_git)
            if found is False:
                return folder, False
            return folder / ghu.relative_path, True
        else:
            path = self.resolve_local_uri(remote.path_or_url)
            return path, path.exists()
