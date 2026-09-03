import os
import shutil
import tempfile

from tko.util.git_hub_url import GitHubUrl
from tko.repository.git_cache import GitCache
from pathlib import Path

from tko.i18n import Msg
from tko.repository.remote import Source, SourceType


_REMOTE_PATH_SOURCE_DIR_NOT_EXISTS = Msg.text(
    pt="Diretório de origem não existe",
    en="Source directory does not exist",
)
_REMOTE_PATH_INDEX_FILE_NOT_EXISTS = Msg.text(
    pt="Arquivo de índice não existe",
    en="Index file does not exist",
)

class SourceResolver:
    def __init__(self, git_cache: GitCache, root_dir: Path):
        self.git_cache: GitCache = git_cache
        self.repo_root_dir: Path = root_dir.resolve()

    def source_work_dir(self, source: Source) -> Path:
        return self.repo_root_dir / source.name

    def is_local_internal(self, source: Source) -> bool:
        if source.source_type != SourceType.LOCAL_FILE:
            return False
        path = self.resolve_local_uri(source.path_or_url)
        return path.is_relative_to(self.repo_root_dir)

    def is_editable_index(self, source: Source) -> bool:
        if source.source_type != SourceType.LOCAL_FILE:
            return False
        return self.is_local_internal(source)

    def source_activity_dir(self, source: Source) -> Path:
        return self.source_work_dir(source)

    def resolve_local_uri(self, uri: str) -> Path:
        path = Path(uri)
        if path.is_absolute():
            return path.resolve()
        return (self.repo_root_dir / path).resolve()

    def serialize_uri(self, source: Source) -> str:
        if source.source_type == SourceType.GIT_SOURCE:
            return source.path_or_url
        path = self.resolve_local_uri(source.path_or_url)
        if path.is_relative_to(self.repo_root_dir):
            return path.relative_to(self.repo_root_dir).as_posix()
        return path.as_posix()

    def materialized_index_file(self, source: Source) -> Path:
        """Return the local snapshot path for a source index."""
        if source.source_type == SourceType.GIT_SOURCE:
            github = GitHubUrl.parse(source.path_or_url)
            if github is None or github.relative_path is None:
                return Path()
            return self.source_work_dir(source) / github.relative_path
        return self.resolve_local_uri(source.path_or_url)

    @staticmethod
    def _copy_snapshot(origin: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                temporary = Path(file.name)
            shutil.copy2(origin, temporary)
            os.replace(temporary, destination)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    
    def resolve_index_file(self, source: Source, load_git: bool) -> tuple[Path , bool]:
        if source.source_type == SourceType.GIT_SOURCE:
            ghu = GitHubUrl.parse(source.path_or_url)
            if ghu is None or ghu.relative_path is None:
                return Path(), False
            folder, found = self.git_cache.get_repository_dir(ghu.repository_url, load_git=load_git)
            cached_index = folder / ghu.relative_path
            snapshot = self.materialized_index_file(source)
            if found and cached_index.exists():
                self._copy_snapshot(cached_index, snapshot)
                return snapshot, True
            return snapshot, snapshot.exists()
        else:
            path = self.resolve_local_uri(source.path_or_url)
            return path, path.exists()
