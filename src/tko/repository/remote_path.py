from tko.repository.git_cache import GitCache
from pathlib import Path

from tko.repository.remote_data import RemoteData, SourceType

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
            return self.git_cache.get_remote_dir(self.data.target, verbose=False)
        path = Path(self.data.target)
        if path.is_absolute():
            return path.resolve()
        return (self.repo_root_dir / path).resolve()

    @property
    def index_file(self) -> Path:
        source_dir = self.source_dir
        if source_dir is None:
            raise ValueError("Source directory does not exist")
        index_path = source_dir / self.data.index
        if index_path.exists():
            return index_path.resolve()
        raise ValueError("Index file does not exist")
    
    @property
    def work_dir(self) -> Path:
        if self.data.is_editable:
            source_dir = self.source_dir
            if source_dir is None:
                raise ValueError("Source directory does not exist")
            return source_dir
        return (self.repo_root_dir / self.data.name).resolve()
