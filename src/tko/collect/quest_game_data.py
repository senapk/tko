from tko.collect.task_game_data import TaskGameData


from typing import Any


class QuestGameData:
    key_str: str = "key"
    value_str: str = "value"
    tasks_str: str = "tasks"
    quests_str: str = "quests"
    leet_str: str = "leet"
    def __init__(self, key: str):
        self.key = key
        self.tasks: list[TaskGameData] = []

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {
            QuestGameData.key_str: self.key,
            QuestGameData.value_str: self.value,
            QuestGameData.tasks_str: [task.to_dict() for task in self.tasks]
        }
        return output

    def load_from_dict(self, json_data: dict[str, Any]):
        self.key = json_data.get(QuestGameData.key_str, self.key)
        self.value = json_data.get(QuestGameData.value_str, self.value)
        tasks_data = json_data.get(QuestGameData.tasks_str, [])
        for task in tasks_data:
            collected_task = TaskGameData().load_from_dict(task)
            self.tasks.append(collected_task)
        return self

    def __str__(self):
        return f'{self.key}, {QuestGameData.value_str}:{self.value}\n' + "\n".join([f"\t{str(t)}" for t in self.tasks])