from tko.game.game import Game
from tko.game.task import Task


def test_game_task_lookup_accepts_legacy_folder_key() -> None:
    game = Game()
    task = Task()
    task.basic.source_name = "course"
    task.basic.key = "labs/carro"
    game.tasks[task.basic.full_key] = task

    assert game.get_task("course@carro") is task
