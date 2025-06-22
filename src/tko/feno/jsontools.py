import enum
import json
import os
from tko.util.decoder import Decoder
from pathlib import Path

def json_norm_join(*args: str) -> str:
    return str(Path(*args).resolve())

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

    def to_json(self) -> dict[str, str]:
        return {
            "name" : self.name,
            "contents": self.contents,
            "type": self.ftype.value,
        }

    # @override
    def __str__(self):
        return self.name + ":" + self.contents + ":" + str(self.ftype.value)

class JsonVPL:
    hide_extension = ".hide"
    exec_extension = ".exec"

    def __init__(self, title: str, description: str):
        self.title: str = title
        self.description: str = description
        self.upload: list[JsonFile] = []
        self.draft: dict[str, list[JsonFile]] = {}
    
    def set_tests(self, exec_file: str):
        data = Decoder.load(exec_file)
        self.upload.append(JsonFile("vpl_evaluate.cases", data, FileType.HIDE))
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
        json_dict = {
            "title": self.title,
            "description": self.description,
            "upload": [x.to_json() for x in self.upload],
            "draft": {k: [x.to_json() for x in v] for k, v in self.draft.items()},
        }
        return json.dumps(json_dict, indent=4, ensure_ascii=True)
    
    def load_drafts(self, cache_draft: str):
        found = False
        if not os.path.isdir(cache_draft):
            return False
        folders: list[str] = os.listdir(cache_draft)
        folders = [f for f in folders if os.path.isdir(os.path.join(cache_draft, f))]
        for lang in folders:
            lang_path = json_norm_join(cache_draft, lang)
            hide_files: list[str] = []
            hide_files_config = os.path.join(lang_path, JsonVPL.hide_extension)
            if os.path.isfile(hide_files_config):
                with open(hide_files_config) as f:
                    hide_files = [x.strip() for x in f.read().splitlines()]
            exec_files: list[str] = []
            exec_files_config = os.path.join(lang_path, JsonVPL.exec_extension)
            if os.path.isfile(exec_files_config):
                with open(exec_files_config) as f:
                    exec_files = [x.strip() for x in f.read().splitlines()]

            for file in os.listdir(lang_path):
                if file.endswith(JsonVPL.hide_extension) or file.endswith(JsonVPL.exec_extension):
                    continue
                ftype = FileType.SHOW
                if file in hide_files:
                    ftype = FileType.HIDE
                elif file in exec_files:
                    ftype = FileType.EXEC
                file_path = json_norm_join(lang_path, file)
                self.add_draft(lang, file_path, ftype)
                found = True
        return found

    # @override
    def __str__(self):
        return self.to_json()
