import yaml # type: ignore
from tko.settings.log_action import LogAction
from tko.util.text import Text

class CacheListener:
    def __init__(self):
        self.cache: dict[str, list[Text]] = {}

    def listener(self, action: LogAction, new_entry: bool = False):
        if action.task_key == "":
            return
        self.cache[action.task_key] = []

    def set_task_cache(self, key: str, lines: list[Text]):
        self.cache[key] = lines

    def get_task_cache(self, key: str) -> list[Text]:
        if key not in self.cache:
            return []
        return self.cache[key]
    