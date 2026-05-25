from __future__ import annotations
from typing import Any
from tko.config.app_settings import AppSettings
from platformdirs import user_data_dir
from pathlib import Path
import yaml #type: ignore

from tko.config.languages_settings import LanguagesSettings
from tko.i18n import Msg, t
from tko.util.rt import RT
from tko.widget.colors import Colors
from tko.util.decoder import Decoder


_SETTINGS_GIT_LABEL_NOT_FOUND = Msg(
    pt="Repositório git label {alias} não encontrado",
    en="Git repository label {alias} not found",
)
_SETTINGS_EMPTY_CONFIG_FILE = Msg(
    pt="Arquivo de configuração vazio: {path}",
    en="Empty config file: {path}",
)
_RESET_SETTINGS_PATH = Msg(
    pt="Arquivo global configuração:",
    en="Global settings file:",
)
_RESET_LANGUAGES_PATH = Msg(
    pt="Configurações de linguagem:",
    en="Language settings:",
)
_SETTINGS_REMOTE_SOURCES_REGISTERED = Msg(
    pt="Fontes de tarefas remotas cadastradas:",
    en="Registered remote task sources:",
)


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
    LANG_FILE = "programming-languages.toml"
    LANG_FILE_SAMPLE = "programming-languages-sample.toml"
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
        self.dict_alias_git: dict[str, str] = self.Defaults.alias_git.copy()  # Explicitly initialize as dict[str, str]
        self.app = AppSettings()
        self.__languages_settings: LanguagesSettings | None = None
        self.colors = Colors()

        self.settings_dir: Path | None = path_dir
        self.data: dict[str, Any] = {}
        self._cached_output: dict[str, Any] = {}  # Cache the output after loading

    def get_languages_settings(self) -> LanguagesSettings:
        if self.__languages_settings is None:
            self.__languages_settings = LanguagesSettings(self.get_languages_file()).load_file_settings()
        return self.__languages_settings
    
    def get_languages_file(self) -> Path:
        return self.get_settings_dir() / self.LANG_FILE

    def get_settings_file(self) -> Path:
        return self.get_settings_dir() / self.CFG_FILE
    
    def get_languages_sample(self) -> Path:
        return self.get_settings_dir() / self.LANG_FILE_SAMPLE


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
        self.get_languages_file().unlink()
        with open(self.get_languages_sample(), "w") as f:
            f.write(LanguagesSettings(self.get_languages_file()).build_file_sample())

        return self


    def set_alias_git(self, alias: str, git_url: str):
        self.dict_alias_git[alias] = git_url
        return self

    def get_alias_git(self, alias: str) -> str:
        if alias in self.dict_alias_git:
            return self.dict_alias_git[alias]
        raise Warning(t(_SETTINGS_GIT_LABEL_NOT_FOUND, alias=alias))

    def has_alias_git(self, alias: str) -> bool:
        return alias in self.dict_alias_git

    def load_settings(self):
        try:
            settings_file = self.get_settings_file()
            content = Decoder.load(settings_file)

            data: Any = yaml.safe_load(content)

            if data is None or not isinstance(data, dict):
                raise FileNotFoundError(t(_SETTINGS_EMPTY_CONFIG_FILE, path=settings_file))
            self.data = data
            self.dict_alias_git: dict[str, str] = dict(self.dict_alias_git) # type: ignore
            if len(self.dict_alias_git.keys()) == 0: # type: ignore
                self.dict_alias_git = self.Defaults.alias_git.copy()
            self.app = AppSettings().from_dict(data.get(self.__appcfg, AppSettings())) # type: ignore
            # self.colors = Colors().from_dict(data.get(self.__colors, Colors())) # type: ignore
            self.__languages_settings = LanguagesSettings(self.get_languages_file()).load_file_settings()

            # Cache the output after loading
            self._cached_output = {
                self.__gitrepos: dict(self.dict_alias_git),  # Explicitly cast to dict[str, str]
                self.__appcfg: self.app.to_dict(),
                # self.__colors: self.colors.to_dict()
            }
        except:
            self.reset()
            self.save_settings()
        return self
    
    def save_settings(self):
        file = self.get_settings_file()
        value: dict[str, Any] = {
            self.__gitrepos: self.dict_alias_git,
            self.__appcfg: self.app.to_dict(),
            # self.__colors: self.colors.to_dict()
        }

        # Compare with cached output instead of reading the file
        if value == self._cached_output:
            return self

        with open(file, "w", encoding="utf-8") as f:
            yaml.dump(value, f)

        # Update the cached output after saving
        self._cached_output = value

        return self

    def __str__(self):
        output: list[str] = []
        output.append(str(RT(t(_RESET_SETTINGS_PATH), "g")))
        output.append("    " + self.get_settings_file().resolve().as_posix())
        output.append(str(RT(t(_RESET_LANGUAGES_PATH), "g")))
        output.append("    " + self.get_languages_file().resolve().as_posix())
        output.append("")
        
        output.append(str(RT(t(_SETTINGS_REMOTE_SOURCES_REGISTERED), "g")))
        max_alias = max([len(key) for key in self.dict_alias_git])
        for key in self.dict_alias_git:
            output.append("- @{} : {}".format(key.ljust(max_alias), self.dict_alias_git[key]))
        output.append("")
        
        app_str = str(self.app)
        return "\n".join(output) + "\n\n" + app_str
