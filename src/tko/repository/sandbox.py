from dataclasses import dataclass

from tko.repository.remote import Remote
from pathlib import Path

REMOTE_NAME: str = "sandbox"
REMOTE_PATH: str = "sandbox.md"

@dataclass(frozen=True, slots=True)
class Sandbox:

    @staticmethod
    def get_sandbox_name() -> str:
        return REMOTE_NAME

    @staticmethod
    def is_sandbox(data: Remote) -> bool:
        return data.name == REMOTE_NAME

    @staticmethod
    def create_default_sandbox_remote() -> Remote:
        return Remote.from_local_file(name=REMOTE_NAME, target=Path(REMOTE_PATH), is_editable=True)