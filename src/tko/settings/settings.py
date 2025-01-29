import os
from typing import Any, Dict
from tko.settings.app_settings import AppSettings
import appdirs  # type: ignore
import yaml # type: ignore

from tko.util.text import Text
from tko.play.colors import Colors
from tko.util.decoder import Decoder

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class Settings:
    CFG_FILE = "settings.yaml"


    def __init__(self):
        self.__remote = "remote"
        self.__appcfg = "appcfg"
        self.__colors = "colors"

        self.dict_alias_remote: Dict[str, str] = {}
        self.app = AppSettings()
        self.colors = Colors()

        self.settings_file = ""

    def set_settings_file(self, path: str):
        self.settings_file = path
        return self

    def get_settings_file(self) -> str:
        if self.settings_file is None or self.settings_file == "":
            self.package_name = "tko"
            default_filename = self.CFG_FILE
            self.settings_file = os.path.join(appdirs.user_data_dir(self.package_name), default_filename)
        
        if not os.path.exists(self.settings_file):
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        return self.settings_file

    def reset(self):
        self.dict_alias_remote = {}
        self.dict_alias_remote["fup"] = "https://github.com/qxcodefup/arcade/blob/master/Readme.md"
        self.dict_alias_remote["ed"] = "https://github.com/qxcodeed/arcade/blob/master/Readme.md"
        self.dict_alias_remote["poo"] = "https://github.com/qxcodepoo/arcade/blob/master/Readme.md"

        self.app = AppSettings()
        self.colors = Colors()
        return self

    def set_alias_remote(self, alias: str, url_or_path: str):
        if not(url_or_path.startswith("http:") or url_or_path.startswith("https:")):
            url_or_path = os.path.abspath(url_or_path)
        self.dict_alias_remote[alias] = url_or_path
        return self

    def has_alias_remote(self, alias: str) -> bool:
        return alias in self.dict_alias_remote

    def get_alias_remote(self, alias: str) -> str:
        if alias in self.dict_alias_remote:
            return self.dict_alias_remote[alias]
        raise Warning(f"Repositório remoto {alias} não encontrado")
    
    def load_settings(self):
        try:
            settings_file = self.get_settings_file() # assure right loading if value == ""
            encoding = Decoder.get_encoding(settings_file)
            with open(settings_file, "r", encoding=encoding) as f:
                data = yaml.safe_load(f)
                self.dict_alias_remote = data.get(self.__remote, {})
                self.app = AppSettings().from_dict(data.get(self.__appcfg, {}))
                self.colors = Colors().from_dict(data.get(self.__colors, {}))
        except (FileNotFoundError, yaml.YAMLError) as e:
            self.reset()
            self.save_settings()
        return self
    
    def save_settings(self):
        file = self.get_settings_file()
        value = {
            self.__remote: self.dict_alias_remote,
            self.__appcfg: self.app.to_dict(),
            self.__colors: self.colors.to_dict()
        }
        with open(file, "w", encoding="utf-8") as f:
            yaml.dump(value, f)
        return self

    def __str__(self):
        output = []
        output.append(str(Text.format("{g}", "Arquivo de configuração:")))
        output.append("- " + self.get_settings_file())
        output.append("")
        output.append(str(Text.format("{g}", "Repositórios remotos cadastrados:")))
        max_alias = max([len(key) for key in self.dict_alias_remote])
        for key in self.dict_alias_remote:
            output.append("- {} : {}".format(key.ljust(max_alias), self.dict_alias_remote[key]))
        output.append("")
        
        app_str = str(self.app)
        return "\n".join(output) + "\n\n" + app_str
