from tko.repository.git_cache import GitCache
from pathlib import Path

from tko.i18n import Msg, t
from tko.repository.remote_data import RemoteData, SourceType


_REMOTE_PATH_SOURCE_DIR_NOT_EXISTS = Msg(
    pt="Diretório de origem não existe",
    en="Source directory does not exist",
)
_REMOTE_PATH_INDEX_FILE_NOT_EXISTS = Msg(
    pt="Arquivo de índice não existe",
    en="Index file does not exist",
)

class RemotePath:
    def __init__(self, git_cache: GitCache,
                 repo_root_dir: Path,
                 data: RemoteData):
        self.git_cache: GitCache = git_cache
        self.repo_root_dir: Path = repo_root_dir.resolve()
        self.data: RemoteData = data

    @property
    def source_dir(self) -> Path | None:
        if self.data.source_type == SourceType.GIT_SOURCE:
            return self.git_cache.get_remote_dir(self.data.target)
        path = Path(self.data.target)
        if path.is_absolute():
            return path.resolve()
        return (self.repo_root_dir / path).resolve()

    @property
    def index_file(self) -> Path:
        source_dir = self.source_dir
        if source_dir is None:
            raise ValueError(t(_REMOTE_PATH_SOURCE_DIR_NOT_EXISTS) )
        index_path = source_dir / self.data.index
        return index_path.resolve()

    
    @property
    def work_dir(self) -> Path:
        if self.data.is_editable:
            source_dir = self.source_dir
            if source_dir is None:
                raise ValueError(t(_REMOTE_PATH_SOURCE_DIR_NOT_EXISTS))
            return source_dir
        return (self.repo_root_dir / self.data.name).resolve()
