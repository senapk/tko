from typing import Any


class TaskGameData:
    default_value: int = 1
    default_leet: bool = True
    
    class Key:
        KEY: str = "key"
        VALUE: str = "value"
        TASK: str = "tasks"
        QUEST: str = "quests"
        LEET: str = "leet"

    def __init__(self, key: str = "", value: int = default_value, is_leet: bool = default_leet):
        self.key = key
        self.value: int = value
        self.leet: bool = is_leet

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        output[TaskGameData.Key.KEY] = self.key
        if self.value != TaskGameData.default_value:
            output[TaskGameData.Key.VALUE] = self.value
        if self.leet != TaskGameData.default_leet:
            output[TaskGameData.Key.LEET] = self.leet
        return output

    def load_from_dict(self, json_data: dict[str, Any]):
        self.key = json_data.get(TaskGameData.Key.KEY, self.key)
        self.value = json_data.get(TaskGameData.Key.VALUE, self.value)
        self.leet = json_data.get(TaskGameData.Key.LEET, self.leet)
        return self

    def __str__(self):
        return f"{self.key}, {TaskGameData.Key.VALUE}:{self.value}, leet:{self.leet}"