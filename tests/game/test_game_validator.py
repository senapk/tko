from tko.game.game_validator import GameValidator
from tko.game.quest import Quest
from tko.game.task import Task


def make_quest(key: str) -> Quest:
    quest = Quest(key.title(), key)
    quest.basic.remote_name = "base"
    return quest


def make_task(key: str) -> Task:
    task = Task()
    task.basic.key = key
    task.basic.remote_name = "base"
    return task


def test_validator_removes_residual_duplicates_from_quests() -> None:
    first = make_quest("first")
    second = make_quest("second")
    first_task = make_task("same")
    duplicate_task = make_task("same")
    unique_task = make_task("unique")
    first.add_task(first_task)
    second.add_task(duplicate_task)
    second.add_task(unique_task)

    validator = GameValidator(
        {first.basic.full_key: first, second.basic.full_key: second}
    ).validate()

    assert first.get_tasks() == [first_task]
    assert second.get_tasks() == [unique_task]
    assert validator.tasks == {
        "base@same": first_task,
        "base@unique": unique_task,
    }


def test_validator_removes_task_that_collides_with_quest_key() -> None:
    quest = make_quest("shared")
    conflicting_task = make_task("shared")
    accepted_task = make_task("accepted")
    quest.add_task(conflicting_task)
    quest.add_task(accepted_task)

    validator = GameValidator({quest.basic.full_key: quest}).validate()

    assert quest.get_tasks() == [accepted_task]
    assert validator.tasks == {"base@accepted": accepted_task}

