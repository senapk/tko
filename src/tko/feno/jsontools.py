import enum
from typing import List, Dict
import json
import os
from tko.util.decoder import Decoder

def json_norm_join(*args: str):
    return os.path.normpath(os.path.join(*args))

class FileType(enum.Enum):
    SHOW = "show" # visível para o aluno como required
    HIDE = "hide" # arquivos extra utilizados na compilação, mas escondidos dos alunos
    EXEC = "exec" # arquivos a serem copiados para a pasta que o código será executado

# Format used to send additional files to VPL
class JsonFile:
    def __init__(self, name: str, contents: str, ftype: FileType):
        self.name: str = name
        self.contents: str = contents
        self.ftype: FileType = ftype

    # @override
    def __str__(self):
        return self.name + ":" + self.contents + ":" + str(self.ftype.value)

class JsonVPL:
    def __init__(self, title: str, description: str):
        self.title: str = title
        self.description: str = description
        self.tests: JsonFile | None = None 
        self.draft: Dict[str, List[JsonFile]] = {}
    
    def set_tests(self, exec_file: str):
        data = Decoder.load(exec_file)
        filename = exec_file.split(os.sep)[-1]
        self.tests = JsonFile(filename, data, FileType.HIDE)
        return self
    
    def add_draft(self, extension: str, exec_file: str, ftype: FileType):
        if extension not in self.draft:
            self.draft[extension] = []
        filename = exec_file.split(os.sep)[-1]
        data = Decoder.load(exec_file)
        jfile = JsonFile(filename, data, ftype)
        self.draft[extension].append(jfile)
        return self

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
    
    def load_drafts(self, cache_draft: str):
        found = False
        if not os.path.isdir(cache_draft):
            return False
        folders: list[str] = os.listdir(cache_draft)
        folders = [f for f in folders if os.path.isdir(os.path.join(cache_draft, f))]
        for lang in folders:
            lang_path = json_norm_join(cache_draft, lang)
            config_file = json_norm_join(lang_path, "config.json")
            config_types: dict[str, list[str]] = { "hide": [], "exec": [] }
            if os.path.isfile(config_file):
                with open(config_file) as f:
                    types = json.load(f)
                    if "hide" in types:
                        config_types["hide"] = types["hide"]
                    if "exec" in types:
                        config_types["exec"] = types["exec"]

            for file in os.listdir(lang_path):
                ftype = FileType.SHOW
                if file in config_types["hide"]:
                    ftype = FileType.HIDE
                elif file in config_types["exec"]:
                    ftype = FileType.EXEC
                file_path = json_norm_join(lang_path, file)
                self.add_draft(lang, file_path, ftype)
                found = True
        return found

    # @override
    def __str__(self):
        return self.to_json()
