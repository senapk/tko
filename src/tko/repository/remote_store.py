from tko.repository.remote_keys import RemoteKeys
from tko.repository.remote_data import RemoteData, SourceType

import os
from typing import Any

class RemoteStore:
    def __init__(self, data: RemoteData):
        self.data: RemoteData = data

    def load_from_dict(self, data: dict[str, Any]):
        Keys = RemoteKeys
        if Keys.NAME in data and isinstance(data[Keys.NAME], str):
            self.data.name = data[Keys.NAME]
        if "alias" in data and isinstance(data["alias"], str): # for backward compatibility
            self.data.name = data["alias"]
        if "database" in data and isinstance(data["database"], str): # for backward compatibility
            self.data.name = data["database"]
        if Keys.TARGET in data and isinstance(data[Keys.TARGET], str):
            self.data.target = data[Keys.TARGET]
        if "link" in data and isinstance(data["link"], str): # for backward compatibility
            self.data.target = data["link"]
            if self.data.target.endswith("README.md"):
                self.data.target = os.path.dirname(self.data.target)
        if Keys.BRANCH in data and isinstance(data[Keys.BRANCH], str):
            self.data.branch = data[Keys.BRANCH]
        else:
            self.data.branch = "master"
        if Keys.TYPE in data and isinstance(data[Keys.TYPE], str):
            type_str = data[Keys.TYPE]
            if type_str == SourceType.LOCAL_FILE.value:
                self.data.source_type = SourceType.LOCAL_FILE
            else:
                self.data.source_type = SourceType.GIT_SOURCE
        else:
            self.data.source_type = SourceType.LOCAL_FILE
        if Keys.QUESTS in data and isinstance(data[Keys.QUESTS], list):
            self.data.quest_filters = {q:"" for q in data[Keys.QUESTS]}
        if Keys.QUESTS in data and isinstance(data[Keys.QUESTS], dict):
            self.data.quest_filters = {q: v for q, v in data[Keys.QUESTS].items()}

        if "filters" in data and isinstance(data["filters"], list): # for backward compatibility
            self.data.quest_filters = {q: "" for q in data["filters"]} # type: ignore
        if "filters" in data and isinstance(data["filters"], dict): # for backward compatibility
            self.data.quest_filters = {q: v for q, v in data["filters"].items()} # type: ignore

        if Keys.WRITEABLE in data and isinstance(data[Keys.WRITEABLE], bool):
            self.data.is_editable = data[Keys.WRITEABLE]
        if self.data.name == "sandbox": # for backward compatibility, to remove in the future
            self.data.is_editable = True
        if Keys.INDEX in data and isinstance(data[Keys.INDEX], str):
            self.data.index = data[Keys.INDEX]
        else:
            self.data.index = "README.md"
        return self

    def save_to_dict(self) -> dict[str, Any]:
        Keys = RemoteKeys
        output: dict[str, Any] = {
            Keys.NAME: self.data.name,
            Keys.TARGET: self.data.target,
            Keys.INDEX: self.data.index,
            Keys.TYPE: self.data.source_type.value,
            Keys.WRITEABLE: self.data.is_editable,
        }
        if self.data.branch is not None and self.data.branch != "master":
            output[Keys.BRANCH] = self.data.branch
        output[Keys.QUESTS] = None if self.data.quest_filters is None else { k: v for k, v in self.data.quest_filters.items() }
        return output