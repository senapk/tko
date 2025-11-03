from __future__ import annotations
import os
from typing import Any
from tko.settings.app_settings import AppSettings
import appdirs  # type: ignore
import yaml #type: ignore

from tko.util.text import Text
from tko.play.colors import Colors
from tko.util.decoder import Decoder
from tko.settings.repository import remove_git_merge_tags

def singleton(class_): # type: ignore
    instances = {}
    def getinstance(*args, **kwargs): # type: ignore
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_] # type: ignore
    return getinstance # type: ignore

@singleton
class Settings:
    CFG_FILE = "settings.yaml"
    class Defaults:
        alias_git = {
            "poo": "https://github.com/qxcodepoo/arcade.git",
            "fup": "https://github.com/qxcodefup/arcade.git",
            "ed": "https://github.com/qxcodeed/arcade.git"
        }

    def __init__(self):
        self.__gitrepos = "gitrepos"
        self.__appcfg = "appcfg"
        self.__colors = "colors"

        self.package_name = 'tko'
        self.dict_alias_git: dict[str, str] = {}
        self.app = AppSettings()
        self.colors = Colors()

        self.settings_file: str = ""
        self.data: dict[str, Any] = {}

    def set_settings_file(self, path: str):
        self.settings_file = path
        return self

    def get_settings_file(self) -> str:
        if self.settings_file == "":
            default_filename = self.CFG_FILE
            self.settings_file = os.path.join(appdirs.user_data_dir(self.package_name), default_filename) # type: ignore
        
        if not os.path.exists(self.settings_file):
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        return self.settings_file
    
    def get_settings_backup_file(self) -> str:
        return self.get_settings_file() + ".backup"

    def reset(self):
        self.dict_alias_git = self.Defaults.alias_git.copy()

        self.app = AppSettings()
        self.colors = Colors()
        return self


    def set_alias_git(self, alias: str, git_url: str):
        self.dict_alias_git[alias] = git_url
        return self

    def get_alias_git(self, alias: str) -> str:
        if alias in self.dict_alias_git:
            return self.dict_alias_git[alias]
        raise Warning(f"Repositório git label {alias} não encontrado")

    def has_alias_git(self, alias: str) -> bool:
        return alias in self.dict_alias_git

    def load_settings(self):
        try:
            settings_file = self.get_settings_file()
            backup_file = self.get_settings_backup_file()

            encoding = Decoder.get_encoding(settings_file)
            with open(settings_file, "r", encoding=encoding) as f:
                lines = f.readlines()
                lines = remove_git_merge_tags(lines)
                data: Any = yaml.safe_load("\n".join(lines))
            if data is None or not isinstance(data, dict):
                with open(backup_file, "r", encoding=encoding) as f:
                    lines = f.readlines()
                    lines = remove_git_merge_tags(lines)
                    data = yaml.safe_load("\n".join(lines))
            if data is None or not isinstance(data, dict):
                raise FileNotFoundError(f"Arquivo de configuração vazio: {settings_file}")
            self.data = data
            self.dict_alias_git = data.get(self.__gitrepos, self.Defaults.alias_git) # type: ignore
            if len(self.dict_alias_git.keys()) == 0: # type: ignore
                self.dict_alias_git = self.Defaults.alias_git.copy()
            self.app = AppSettings().from_dict(data.get(self.__appcfg, AppSettings())) # type: ignore
            self.colors = Colors().from_dict(data.get(self.__colors, Colors())) # type: ignore
        except:
            self.reset()
            self.save_settings()
        return self
    
    def save_settings(self):
        file = self.get_settings_file()
        value: dict[str, Any] = {
            self.__gitrepos: self.dict_alias_git,
            self.__appcfg: self.app.to_dict(),
            self.__colors: self.colors.to_dict()
        }
        backup_file = self.get_settings_backup_file()
        if os.path.exists(file):
            if os.path.exists(backup_file):
                os.remove(backup_file)
            os.rename(file, backup_file)
        with open(file, "w", encoding="utf-8") as f:
            yaml.dump(value, f)
        return self

    # @override
    def __str__(self):
        output: list[str] = []
        output.append(str(Text.format("{g}", "Arquivo de configuração:")))
        output.append("- " + self.get_settings_file())
        output.append("")
        output.append(str(Text.format("{g}", "Repositórios remotos cadastrados:")))
        max_alias = max([len(key) for key in self.dict_alias_git])
        for key in self.dict_alias_git:
            output.append("- {} : {}".format(key.ljust(max_alias), self.dict_alias_git[key]))
        output.append("")
        
        app_str = str(self.app)
        return "\n".join(output) + "\n\n" + app_str
