from typing import Any, Dict
import os
import tempfile
from ..util.remote import RemoteCfg, Absolute


class RepSettings:
    expanded = "expanded"
    new_items = "new_items"
    tasks = "tasks"
    flags = "flags"
    lang = "lang"

    defaults = {
        expanded: [],
        tasks: {},
        flags: {},
        new_items: [],
        lang: ""
    }

    def __init__(self, file: str = ""):
        self.url: str = ""
        self.file: str = ""
        self.data: Dict[str, Any] = {}
        if file != "":
            self.file = os.path.abspath(file)

    def get(self, key: str) -> Any:
        if key not in self.defaults:
            raise ValueError(f"Key {key} not found in RepSettings")
        value = self.data.get(key, RepSettings.defaults[key])
        if type(value) != type(RepSettings.defaults[key]):
            return RepSettings.defaults[key]
        return value

    def set(self, key: str, value: Any):
        self.data[key] = value
        return self

    def get_file(self) -> str:
        # arquivo existe e é local
        if self.file != "" and os.path.exists(self.file) and self.url == "":
            return self.file

        # arquivo não existe e é remoto
        if self.url != "" and (self.file == "" or not os.path.exists(self.file)):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                filename = f.name
                cfg = RemoteCfg(self.url)
                cfg.download_absolute(filename)
            return filename

        if self.file != "" and os.path.exists(self.file) and self.url != "":
            content = open(self.file, encoding="utf-8").read()
            content = Absolute.relative_to_absolute(content, RemoteCfg(self.url))
            with tempfile.NamedTemporaryFile(delete=False) as f:
                filename = f.name
                f.write(content.encode("utf-8"))
            return filename

        raise ValueError("fail: file not found or invalid settings to download repository file")

    def set_file(self, file: str):
        self.file = os.path.abspath(file)
        return self

    def set_url(self, url: str):
        self.url = url
        return self

    def to_dict(self):
        return {
            "url": self.url,
            "file": self.file,
            "data": self.data
        }

    def from_dict(self, data: Dict[str, Any]):
        self.url = data.get("url", "")
        self.file = data.get("file", "")
        self.data = data.get("data", {})
        return self

    def __str__(self) -> str:
        return (
            f"url: {self.url}\n"
            f"file: {self.file}\n"
            f"data: {self.data}\n"
        )
