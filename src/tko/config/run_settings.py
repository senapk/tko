
from dataclasses import dataclass
from pathlib import Path

from tko.repository.git_cache import UpdateMode

@dataclass
class RunSettings:
    changedir: Path = Path(".")
    local_cache: bool = False
    debug_mode: bool = False
    force_update: bool = False
    force_offline: bool = False
    width: int | None = None

    @property
    def update_mode(self):
        mode = UpdateMode.IF_OLDER
        if self.force_update:
            mode = UpdateMode.ALWAYS
        elif self.force_offline:
            mode = UpdateMode.NEVER
        return mode
