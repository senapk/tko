from tko.game.game import Game
from tko.game.task import Task


def test_game_task_lookup_requires_exact_key_after_migration() -> None:
    game: Game = Game()
    task: Task = Task()
    task.basic.source_name = "course"
    task.basic.key = "labs/carro"
    game.tasks[task.basic.full_key] = task

    assert game.get_task("course@carro") is None
    assert game.get_task("course@labs/carro") is task
