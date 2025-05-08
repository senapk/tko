import yaml # type: ignore
from tko.settings.log_action import LogAction
        

class CacheListener:
    def __init__(self):
        self.cache: dict[str, list[str]] = {}

    def listener(self, action: LogAction, new_entry: bool = False):
        if action.task_key == "":
            return
        self.cache[action.task_key] = []

    def set_task_cache(self, key: str, lines: list[str]):
        self.cache[key] = lines

    def get_task_cache(self, key: str) -> list[str]:
        if key not in self.cache:
            return []
        return self.cache[key]
    