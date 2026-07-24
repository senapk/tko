from dataclasses import dataclass

from tko.repository.remote import Remote

REMOTE_NAME: str = "sandbox"

@dataclass(frozen=True, slots=True)
class Sandbox:

    @staticmethod
    def get_sandbox_name() -> str:
        return REMOTE_NAME

    @staticmethod
    def is_sandbox(data: Remote) -> bool:
        return data.name == REMOTE_NAME