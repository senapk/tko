from tko.collect.task_game_data import TaskGameData


from typing import Any


class QuestGameData:
    class Key:
        KEY: str = "key"
        VALUE: str = "value"
        TASKS: str = "tasks"
        QUESTS: str = "quests"

    def __init__(self, key: str):
        self.key = key
        self.tasks: list[TaskGameData] = []

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {
            QuestGameData.Key.KEY: self.key,
            QuestGameData.Key.VALUE: self.value,
            QuestGameData.Key.TASKS: [task.to_dict() for task in self.tasks]
        }
        return output

    def load_from_dict(self, json_data: dict[str, Any]):
        self.key = json_data.get(QuestGameData.Key.KEY, self.key)
        self.value = json_data.get(QuestGameData.Key.VALUE, self.value)
        tasks_data = json_data.get(QuestGameData.Key.TASKS, [])
        for task in tasks_data:
            collected_task = TaskGameData().load_from_dict(task)
            self.tasks.append(collected_task)
        return self

    def __str__(self):
        return f'{self.key}, {QuestGameData.Key.VALUE}:{self.value}\n' + "\n".join([f"\t{str(t)}" for t in self.tasks])