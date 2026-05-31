from tko.collect.collect_actions import CollectActions
from tko.collect.collected import Collected
from tko.repository.repository_builder import RepositoryBuilder


import json
from pathlib import Path

class CollectParams:
    def __init__(self):
        self.folder: Path = Path()
        self.width: int = 10
        self.height: int = 10
        self.daily: bool = False
        self.resume: bool = False
        self.history: bool = False
        self.game: bool = False
        self.log: bool = False
        self.json_output: bool = False
        self.colored: int = 1

class CollectSingle:
    @staticmethod
    def collect_to_json(repo_folder: Path, daily: bool = True, resume: bool = True, history: bool = True, game: bool = True) -> str:
        params = CollectParams()
        params.folder = repo_folder
        params.daily = daily
        params.resume = resume
        params.history = history
        params.game = game
        params.json_output = True # dont echo
        results: Collected = CollectSingle.collect(params)
        return json.dumps(results.get_dict(), indent=4, ensure_ascii=False)

    @staticmethod
    def collect(param: CollectParams) -> Collected:
        rb = RepositoryBuilder()
        rb.dir_path(param.folder).global_cache(True).load_config_and_game().verbose()
        repo, _ = rb.build()
        data = Collected()
        if repo is None:
            return data

        if param.daily:
            graph = CollectActions.daily_graph(repo, param.width, param.height, param.colored == 1)
            data.daily_graph = graph
            if not param.json_output:
                print(graph)

        if param.resume:
            resume_data = CollectActions.resume(repo)
            data.task_resume = resume_data
            if not param.json_output:
                task_pad = max((len(key) for key in data.task_resume.keys()), default=0) + 2
                quest_pad = max((len(item.quest) for item in data.task_resume.values()), default=0) + 2
                for _, item in resume_data.items():
                    text = str(item.get_kv(include_key=False, include_quest=False)).replace("'", "").replace("{", "").replace("}", "")
                    print(f"{item.key:<{task_pad}} {item.quest:<{quest_pad}} {text}")

        if param.log:
            log_data = repo.logger.history.get_entries()
            data.full_log = [str(entry) for entry in log_data]
            if not param.json_output:
                for entry in log_data:
                    print(entry)

        if param.history:
            data.task_history = repo.logger.tasks.mount_task_history(repo.game)
            if not param.json_output:
                task_pad = max((len(item.key) for item in data.task_history), default=0) + 2
                quest_pad = max((len(item.quest) for item in data.task_history), default=0) + 2                
                for item in data.task_history:
                    item.resume.events = 0 # hide events for history
                    text = str(item.get_kv(include_key=False, include_quest=False)).replace("'", "").replace("{", "").replace("}", "")
                    print(f"{item.key:<{task_pad}} {item.quest:<{quest_pad}} {text}")

        if param.game:
            game_data = CollectActions.load_game_as_quest_list(repo)
            data.game_structure = game_data
            if not param.json_output:
                for quest in game_data:
                    print(str(quest))
        return data