import enum
from typing import List, Dict
import json
import os
from tko.util.decoder import Decoder


def json_norm_join(*args):
    return os.path.normpath(os.path.join(*args))

# Format used to send additional files to VPL
class JsonFile:
    def __init__(self, name: str, contents: str):
        self.name: str = name
        self.contents: str = contents
        self.encoding: int = 0

    def __str__(self):
        return self.name + ":" + self.contents + ":" + str(self.encoding)

class JsonFileType(enum.Enum):
    UPLOAD = 1
    KEEP = 2
    REQUIRED = 3


class JsonVPL:
    def __init__(self, title: str, description: str):
        self.title: str = title
        self.description: str = description
        self.upload: List[JsonFile] = []
        self.keep: List[JsonFile] = []
        self.required: List[JsonFile] = []
        self.draft: Dict[str, List[JsonFile]] = {}

    def __add_file(self, ftype: JsonFileType, exec_file: str, rename=""):
        data = Decoder.load(exec_file)
        file_name = rename if rename != "" else exec_file.split(os.sep)[-1]
        jfile = JsonFile(file_name, data)
        if ftype == JsonFileType.UPLOAD:
            self.upload.append(jfile)
        elif ftype == JsonFileType.KEEP:
            self.keep.append(jfile)
        else:
            self.required.append(jfile)
    
    def set_cases(self, exec_file: str):
        self.__add_file(JsonFileType.UPLOAD, exec_file, "vpl_evaluate.cases")
        return self

    def add_upload(self, exec_file: str, rename=""):
        self.__add_file(JsonFileType.UPLOAD, exec_file, rename)
        return self

    def add_keep(self, exec_file: str, rename=""):
        self.__add_file(JsonFileType.KEEP, exec_file, rename)
        return self

    def add_required(self, exec_file: str, rename=""):
        self.__add_file(JsonFileType.REQUIRED, exec_file, rename)
        return self
    
    def add_draft(self, extension: str, exec_file: str):
        if extension not in self.draft:
            self.draft[extension] = []
        data = Decoder.load(exec_file)
        jfile = JsonFile(exec_file.split(os.sep)[-1], data)
        self.draft[extension].append(jfile)
        return self

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def load_config_json(self, cfg_json: str, source: str):
        if os.path.isfile(cfg_json):
            with open(cfg_json) as f:
                cfg = json.load(f)
                if "upload" in cfg:
                    for file in cfg["upload"]:
                        self.add_upload(json_norm_join(source, file))
                if "keep" in cfg:
                    for file in cfg["keep"]:
                        self.add_keep(json_norm_join(source, file))
                if "required" in cfg:
                    for file in cfg["required"]:
                        self.add_required(json_norm_join(source, file))
            return True
        return False
    
    def load_drafts(self, cache_draft: str):
        found = False
        if not os.path.isdir(cache_draft):
            return False
        for lang in os.listdir(cache_draft):
            lang_path = json_norm_join(cache_draft, lang)
            if os.path.isdir(lang_path):
                for file in os.listdir(lang_path):
                    file_path = json_norm_join(lang_path, file)
                    self.add_draft(lang, file_path)
                    found = True
        return found

    def __str__(self):
        return self.to_json()
