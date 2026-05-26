from tko.collect.collect_actions import CMD_COLLECT_REPO_NOT_FOUND, CollectActions
from tko.i18n import t
from tko.collect.collected import Collected
from tko.repository.repository import Repository


import json
import os
from pathlib import Path

class CollectParams:
    def __init__(self):
        self.folder: Path = Path()
        self.width: int = 10
        self.height: int = 10
        self.daily: bool = False
        self.resume: bool = False
        self.game: bool = False
        self.log: bool = False
        self.json_output: bool = False
        self.colored: int = 1

class CollectSingle:
    @staticmethod
    def collect_to_json(repo_folder: Path, daily: bool = True, resume: bool = True, game: bool = True) -> str:
        params = CollectParams()
        params.folder = repo_folder
        params.daily = daily
        params.resume = resume
        params.game = game
        params.json_output = True # dont echo
        results: Collected = CollectSingle.collect(params)
        return json.dumps(results.to_dict(), indent=4, ensure_ascii=False)

    @staticmethod
    def collect(param: CollectParams) -> Collected:
        rep = Repository(param.folder)
        if not rep.found():
            path = os.path.abspath(param.folder)
            print(t(CMD_COLLECT_REPO_NOT_FOUND, path=path))
            return Collected()
        rep.set_global_cache()
        from tko.repository.repository_loader import RepositoryLoader
        from tko.repository.game_coordinator import GameCoordinator
        RepositoryLoader(rep).load_config()
        GameCoordinator(rep).load_game(verbose=True)
        data = Collected()

        if param.daily:
            graph = CollectActions.daily_graph(rep, param.width, param.height, param.colored == 1)
            data.graph = graph
            if not param.json_output:
                print(graph)

        if param.resume:
            resume_data = CollectActions.resume(rep)
            data.resume = resume_data
            if not param.json_output:
                for key, value in resume_data.items():
                    print(f"{key}: {value.to_dict()}")

        if param.log:
            log_data = rep.logger.history.get_entries()
            data.log = [str(entry) for entry in log_data]
            if not param.json_output:
                for entry in log_data:
                    print(entry)

        if param.game:
            game_data = CollectActions.load_game_as_quest_list(rep)
            data.quests = game_data
            if not param.json_output:
                for quest in game_data:
                    print(str(quest))
        return data