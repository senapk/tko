from __future__ import annotations
from pathlib import Path
from tko.repository.remote_data import RemoteData
from tko.repository.remote_path import RemotePath
from tko.repository.remote_store import RemoteStore
from tko.repository.git_cache import GitCache
from tko.i18n import Msg
from typing import Any

from tko.repository.remote_sandbox import REMOTE_SANDBOX_INDEX, REMOTE_SANDBOX_NAME, REMOTE_SANDBOX_TARGET

_REMOTE_GIT_CACHE_ROOT_REQUIRED = Msg(
    pt="Git cache and root dir must be set to resolve the path",
    en="Git cache and root dir must be set to resolve the path",
)
_REMOTE_SANDBOX_ONLY_TRUE = Msg(
    pt="Sandbox source só pode ser definido como True",
    en="Sandbox source can only be set to True",
)

class Remote:
    def __init__(self, alias: str = "", git_cache: GitCache | None = None):
        self.data = RemoteData(name=alias)
        self.git_cache: GitCache | None = git_cache
        self.root_dir: Path | None = None

    @property
    def path(self) -> RemotePath:
        if self.git_cache is None or self.root_dir is None:
            raise ValueError(str(_REMOTE_GIT_CACHE_ROOT_REQUIRED))
        return RemotePath(git_cache=self.git_cache, repo_root_dir=self.root_dir, data=self.data)

    
    def load_from_dict(self, data: dict[str, Any]) -> Remote:
        RemoteStore(self.data).load_from_dict(data)
        return self

    def save_to_dict(self) -> dict[str, Any]:
        return RemoteStore(self.data).save_to_dict()

    @property
    def is_sandbox(self) -> bool:
        return self.data.name == REMOTE_SANDBOX_NAME

    @is_sandbox.setter
    def is_sandbox(self, value: bool):
        if value:
            self.data.name = REMOTE_SANDBOX_NAME
            self.data.set_local_source(target=Path(REMOTE_SANDBOX_TARGET), is_editable=True, index=REMOTE_SANDBOX_INDEX)
        else:
            raise ValueError(str(_REMOTE_SANDBOX_ONLY_TRUE))
