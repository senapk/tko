import json
from typing import Any, Dict
from .rep_settings import RepData, RepSource
from .geral_settings import GeralSettings
import os

class Settings:
    def __init__(self):
        self.reps: Dict[str, RepSource] = {}
        self.geral = GeralSettings()

    def init_default_reps(self):
        self.reps["fup"] = RepSource(url = "https://github.com/qxcodefup/arcade/blob/master/Readme.md")
        self.reps["ed"] = RepSource(url = "https://github.com/qxcodeed/arcade/blob/master/Readme.md")
        self.reps["poo"] = RepSource(url = "https://github.com/qxcodepoo/arcade/blob/master/Readme.md")

        for key in self.reps:
            repdata = self.get_rep_data(key)
            repdata.save_data_to_json()
        return self

    def __get_rep_file_path(self, course: str) -> str:
        return os.path.join(self.geral.get_rootdir(), course, ".rep.json")   

    def get_rep_source(self, course: str) -> RepSource:
        if course in self.reps:
            return self.reps[course]
        raise Warning(f"Curso {course} não encontrado")

    def get_rep_data(self, course: str) -> RepData:
        cfg_file = self.__get_rep_file_path(course)
        rep_data = RepData(cfg_file)
        if os.path.exists(cfg_file):
            return rep_data.load_data_from_json()
        return rep_data.load_defaults()
  
    def to_dict(self) -> Dict[str, Any]:
        return {
            "reps": {k: v.to_dict() for k, v in self.reps.items()},
            "geral": self.geral.to_dict()
        }

    def from_dict(self, data: Dict[str, Any]):
        self.reps = {k: RepSource().from_dict(v) for k, v in data.get("reps", {}).items()}
        self.geral = GeralSettings().from_dict(data.get("geral", {}))
        return self
    
    def save_to_json(self, file: str):
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)
        return self

    def __str__(self):
        output = ["Repositories:"]
        maxlen = max([len(key) for key in self.reps])
        for key in self.reps:
            prefix = f"- {key.ljust(maxlen)}"
            if self.reps[key].file and self.reps[key].url:
                output.append(f"{prefix} : dual   : {self.reps[key].url} ; {self.reps[key].file}")
            elif self.reps[key].url:
                output.append(f"{prefix} : remote : {self.reps[key].url}")
            else:
                output.append(f"{prefix} : local  : {self.reps[key].file}")
        return "\n".join(output)
