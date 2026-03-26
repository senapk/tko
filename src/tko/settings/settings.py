from __future__ import annotations
from typing import Any
from tko.settings.app_settings import AppSettings
from platformdirs import user_data_dir
from pathlib import Path
import yaml #type: ignore

from tko.settings.languages_settings import LanguagesSettings
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
    LANG_FILE = "languages.toml"
    class Defaults:
        alias_git = {
            "poo": "https://github.com/qxcodepoo/arcade.git",
            "fup": "https://github.com/qxcodefup/arcade.git",
            "ed": "https://github.com/qxcodeed/arcade.git"
        }

    # use path_dir None to use default path for tko settings, or set a custom path for the settings file
    def __init__(self, path_dir: Path | None):
        self.__gitrepos = "gitrepos"
        self.__appcfg = "appcfg"
        self.__colors = "colors"

        self.package_name = 'tko'
        self.dict_alias_git: dict[str, str] = {}
        self.app = AppSettings()
        self.__languages_settings: LanguagesSettings | None = None
        self.colors = Colors()

        self.settings_dir: Path | None = path_dir
        self.data: dict[str, Any] = {}

    def get_languages_settings(self) -> LanguagesSettings:
        if self.__languages_settings is None:
            self.__languages_settings = LanguagesSettings(self.get_languages_file()).load_file_settings()
        return self.__languages_settings
    
    def get_languages_file(self) -> Path:
        return self.get_settings_dir() / self.LANG_FILE

    def get_settings_file(self) -> Path:
        return self.get_settings_dir() / self.CFG_FILE

    def get_settings_dir(self) -> Path:
        if self.settings_dir is None:
            self.settings_dir = Path(user_data_dir(self.package_name))
        if not self.settings_dir.exists():
            self.settings_dir.mkdir(parents=True, exist_ok=True)
        return self.settings_dir

    def reset(self):
        self.dict_alias_git = self.Defaults.alias_git.copy()
        self.app = AppSettings()
        self.colors = Colors()
        self.__languages_settings = LanguagesSettings(self.get_languages_file()).reset().save_file_settings()

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
            content = Decoder.load(settings_file)

            lines = content.splitlines()
            lines = remove_git_merge_tags(lines)
            data: Any = yaml.safe_load("\n".join(lines))

            if data is None or not isinstance(data, dict):
                raise FileNotFoundError(f"Arquivo de configuração vazio: {settings_file}")
            self.data = data
            self.dict_alias_git = data.get(self.__gitrepos, self.Defaults.alias_git) # type: ignore
            if len(self.dict_alias_git.keys()) == 0: # type: ignore
                self.dict_alias_git = self.Defaults.alias_git.copy()
            self.app = AppSettings().from_dict(data.get(self.__appcfg, AppSettings())) # type: ignore
            self.colors = Colors().from_dict(data.get(self.__colors, Colors())) # type: ignore
            self.__languages_settings = LanguagesSettings(self.get_languages_file()).load_file_settings()
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
        with open(file, "w", encoding="utf-8") as f:
            yaml.dump(value, f)
        self.get_languages_settings().save_file_settings()
        return self

    def __str__(self):
        output: list[str] = []
        output.append(str(Text.format("{g}", "Arquivo global configuração:")))
        output.append("- " + str(self.get_settings_file()))
        output.append("- " + str(self.get_languages_file()))
        output.append("")
        output.append(str(Text.format("{g}", "Fontes de tarefas remotas cadastradas:")))
        max_alias = max([len(key) for key in self.dict_alias_git])
        for key in self.dict_alias_git:
            output.append("- @{} : {}".format(key.ljust(max_alias), self.dict_alias_git[key]))
        output.append("")
        
        app_str = str(self.app)
        return "\n".join(output) + "\n\n" + app_str
