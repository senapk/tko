import json
from typing import Any, Dict
from .rep_settings import RepSettings
from .geral_settings import GeralSettings

class Settings:
    def __init__(self):
        self.reps: Dict[str, RepSettings] = {}
        self.geral = GeralSettings()
        self.reps["fup"] = RepSettings().load_defaults().set_url("https://github.com/qxcodefup/arcade/blob/master/Readme.md")
        self.reps["ed"] = RepSettings().load_defaults().set_url("https://github.com/qxcodeed/arcade/blob/master/Readme.md")
        self.reps["poo"] = RepSettings().load_defaults().set_url("https://github.com/qxcodepoo/arcade/blob/master/Readme.md")

    def get_repo(self, course: str) -> RepSettings:
        if course not in self.reps:
            raise ValueError(f"Course {course} not found in settings")
        return self.reps[course]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "reps": {k: v.to_dict() for k, v in self.reps.items()},
            "geral": self.geral.to_dict()
        }

    def from_dict(self, data: Dict[str, Any]):
        self.reps = {k: RepSettings().from_dict(v) for k, v in data.get("reps", {}).items()}
        self.geral = GeralSettings().from_dict(data.get("geral", {}))
        return self
    
    def save_to_json(self, file: str):
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

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

