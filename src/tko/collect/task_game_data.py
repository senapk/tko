from typing import Any


class TaskGameData:
    default_value: int = 1
    default_leet: bool = True
    key_str: str = "key"
    value_str: str = "value"
    tasks_str: str = "tasks"
    quests_str: str = "quests"
    leet_str: str = "leet"
    def __init__(self, key: str = "", value: int = default_value, is_leet: bool = default_leet):
        self.key = key
        self.value: int = value
        self.leet: bool = is_leet

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        output[TaskGameData.key_str] = self.key
        if self.value != TaskGameData.default_value:
            output[TaskGameData.value_str] = self.value
        if self.leet != TaskGameData.default_leet:
            output[TaskGameData.leet_str] = self.leet
        return output

    def load_from_dict(self, json_data: dict[str, Any]):
        self.key = json_data.get(TaskGameData.key_str, self.key)
        self.value = json_data.get(TaskGameData.value_str, self.value)
        self.leet = json_data.get(TaskGameData.leet_str, self.leet)
        return self

    def __str__(self):
        return f"{self.key}, {TaskGameData.value_str}:{self.value}, leet:{self.leet}"