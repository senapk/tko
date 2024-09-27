import json
from typing import Any, Dict
from .rep_settings import RepData, RepSource
from .app_settings import AppSettings
import os
import appdirs

from tko.util.text import Text
from tko.play.colors import Colors
from tko.util.raw_terminal import RawTerminal

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class Settings:
    def __init__(self):
        self.reps: Dict[str, RepSource] = {}
        self.app = AppSettings()
        self.colors = Colors()

        self.settings_file = ""

    def set_settings_file(self, path: str):
        self.settings_file = path
        return self

    def get_settings_file(self) -> str:
        if self.settings_file is None or self.settings_file == "":
            self.package_name = "tko"
            default_filename = "settings.json"
            self.settings_file = os.path.abspath(default_filename)  # backup for replit, dont remove
            self.settings_file = os.path.join(appdirs.user_data_dir(self.package_name), default_filename)
        
        if not os.path.exists(self.settings_file):
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        return self.settings_file

    def reset(self):
        self.reps = {}
        self.reps["fup"] = RepSource(url = "https://github.com/qxcodefup/arcade/blob/master/Readme.md")
        self.reps["ed"] = RepSource(url = "https://github.com/qxcodeed/arcade/blob/master/Readme.md")
        self.reps["poo"] = RepSource(url = "https://github.com/qxcodepoo/arcade/blob/master/Readme.md")

        # for key in self.reps:
        #     repdata = self.get_rep_data(key)
        #     repdata.save_data_to_json()

        self.app = AppSettings()
        self.colors = Colors()
        return self

    def __get_old_rep_file_path(self, course: str) -> str:
        return os.path.join(self.app.get_rootdir(), course, ".rep.json")

    def __get_new_rep_file_path(self, course: str) -> str:
        return os.path.join(self.app.get_rootdir(), course, "rep.json")

    def get_rep_source(self, course: str) -> RepSource:
        if course in self.reps:
            return self.reps[course]
        raise Warning(f"Curso {course} não encontrado")

    def get_rep_data(self, course: str) -> RepData:
        old_cfg_file = self.__get_old_rep_file_path(course)
        new_cfg_file = self.__get_new_rep_file_path(course)
        if os.path.exists(old_cfg_file):
            os.rename(old_cfg_file, new_cfg_file)
        
        rep_data = RepData(self.app.get_rootdir(), course, new_cfg_file)
        if os.path.exists(new_cfg_file):
            return rep_data.load_data_from_json()
        return rep_data.load_defaults()
  
    # def to_dict(self) -> Dict[str, Any]:
    #     return {
    #         "reps": {k: v.to_dict() for k, v in self.reps.items()},
    #         "geral": self.app.to_dict()
    #     }
    
    def load_settings(self):
        try:
            settings_file = self.get_settings_file() # assure right loading if value == ""
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.reps = {k: RepSource().from_dict(v) for k, v in data.get("reps", {}).items()}
                self.app = AppSettings().from_dict(data.get("geral", {}))
                self.colors = Colors().from_dict(data.get("colors", {}))
        except (FileNotFoundError, json.decoder.JSONDecodeError) as _e:
            self.reset()
            self.save_settings()
        return self

    # def from_dict(self, data: Dict[str, Any]):
    #     self.reps = {k: RepSource().from_dict(v) for k, v in data.get("reps", {}).items()}
    #     self.app = AppSettings().from_dict(data.get("geral", {}))
    #     return self

    def check_rootdir(self):
        if self.app._rootdir != "":
            return
        print(Text().add("Pasta padrão para download de arquivos ").addf("r", "precisa").add(" ser definida."))
        here_cwd = os.getcwd()
        qxcode = os.path.join(os.path.expanduser("~"), "qxcode")

        while True:
            print(Text().addf("r", "1").add(" - ").add(here_cwd))
            print(Text().addf("r", "2").add(" - ").add(qxcode))
            print(Text().addf("r", "3").add(" - ").add("Outra pasta"))
            print(Text().add("Default ").addf("r", "1").add(": "), end="")
            op = input()
            if op == "":
                op = "1"
            if op == "1":
                home_qxcode = here_cwd
                break
            if op == "2":
                home_qxcode = qxcode
                break
            if op == "3":
                print(Text().addf("y", "Navegue até o diretório desejado e execute o tko novamente."))
                exit(1)

        if not os.path.exists(home_qxcode):
            os.makedirs(home_qxcode)
        print("Pasta padrão para download de arquivos foi definida em: " + home_qxcode)
        print(RawTerminal.centralize("", "-"))
        self.app._rootdir = home_qxcode
        self.save_settings();
        return self
    
    def check_rep_alias(self, rep_alias: str):
        if rep_alias == "__ask":
            last = self.app.get_last_rep()
            if last != "" and last in self.reps:
                rep_alias = last
            else:
                print("Escolha um dos repositórios para abrir:")
                options: Dict[int, str] = {}
                for i, alias in enumerate(self.reps, start=1):
                    print(Text().addf("r", str(i)).add(f" - {alias}"))
                    options[i] = alias
                while True:
                    try:
                        print("Digite o número do repositório desejado: ", end="")
                        index = int(input())
                        if index in options:
                            rep_alias = options[index]
                            self.app.set_last_rep(rep_alias)
                            self.save_settings()
                            break
                    except ValueError:
                        pass
                    print("Digite um número válido")
        return rep_alias
    
    def save_settings(self):
        file = self.get_settings_file()
        value = {
            "reps": {k: v.to_dict() for k, v in self.reps.items()},
            "geral": self.app.to_dict(),
            "colors": self.colors.to_dict()
        }
        with open(file, "w", encoding="utf-8") as f:
            json.dump(value, f, indent=4)
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
