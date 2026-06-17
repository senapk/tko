
from dataclasses import dataclass
from pathlib import Path

from tko.repository.git_cache import UpdateMode

@dataclass
class RunSettings:
    changedir: Path = Path(".")
    monochrome: bool = False
    local_cache: bool = False
    debug_mode: bool = False
    width: int | None = None
    update_mode = UpdateMode.IF_OLDER


    @property
    def force_update(self) -> bool:
        return self.update_mode == UpdateMode.ALWAYS
    
    @force_update.setter
    def force_update(self, value: bool) -> None:
        if value:
            self.update_mode = UpdateMode.ALWAYS
        elif self.update_mode == UpdateMode.ALWAYS:
            self.update_mode = UpdateMode.IF_OLDER

    @property
    def force_offline(self) -> bool:
        return self.update_mode == UpdateMode.NEVER
    
    @force_offline.setter
    def force_offline(self, value: bool) -> None:
        if value:
            self.update_mode = UpdateMode.NEVER
        elif self.update_mode == UpdateMode.NEVER:
            self.update_mode = UpdateMode.IF_OLDER
