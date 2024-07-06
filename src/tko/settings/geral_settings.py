from typing import Any, Dict


class GeralSettings:
    rootdir = "rootdir"
    ascii = "ascii"
    color = "color"
    diffdown = "diffdown"
    sidesize = "sidesize"
    lang = "lang"

    defaults = {
        rootdir: "",
        ascii: False,
        color: True,
        diffdown: True,
        sidesize: 80,
        lang: ""
    }

    def __init__(self):
        self.data: Dict[str, Any] = {}

    def set(self, key: str, value: Any):
        self.data[key] = value
        return self
    
    def get(self, key: str) -> str:
        if key not in self.defaults:
            raise ValueError(f"Key {key} not found in GeralSettings")
        return self.data.get(key, GeralSettings.defaults[key])

    def to_dict(self) -> Dict[str, Any]:
        return self.data
        
    
    def from_dict(self, data: Dict[str, Any]):
        self.data = data
        return self

    def __str__(self) -> str:
        return str(self.data)
