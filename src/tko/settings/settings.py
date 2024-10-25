import json
from typing import Any, Dict
from .repository import Repository
from .app_settings import AppSettings
import os
import appdirs

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
    CFG_FILE = "settings.json"


    def __init__(self):
        self.__remote = "remote"
        self.__folder = "folders"
        self.__appcfg = "appcfg"
        self.__colors = "colors"

        self.dict_alias_remote: Dict[str, str] = {}
        self.dict_alias_folder: Dict[str, str] = {}
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
            self.settings_file = os.path.abspath(default_filename)  # backup for replit, dont remove
            self.settings_file = os.path.join(appdirs.user_data_dir(self.package_name), default_filename)
        
        if not os.path.exists(self.settings_file):
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        return self.settings_file

    def reset(self):
        self.dict_alias_remote = {}
        self.dict_alias_remote["fup"] = "https://github.com/qxcodefup/arcade/blob/master/Readme.md"
        self.dict_alias_remote["ed"] = "https://github.com/qxcodeed/arcade/blob/master/Readme.md"
        self.dict_alias_remote["poo"] = "https://github.com/qxcodepoo/arcade/blob/master/Readme.md"
        self.dict_alias_folder = {}
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

    def set_alias_folder(self, alias: str, folder: str):
        self.dict_alias_folder[alias] = os.path.abspath(folder)
        return self
    
    def has_alias_folder(self, course: str) -> bool:
        return course in self.dict_alias_folder

    def del_alias_folder(self, course: str):
        if course in self.dict_alias_folder:
            del self.dict_alias_folder[course]
        return self

    def get_alias_folder(self, course: str) -> str:
        if course in self.dict_alias_folder:
            folder = self.dict_alias_folder[course]
            if not isinstance(folder, str):
                self.reset()
                self.save_settings()
                return self.get_alias_folder(course)
            else:
                return folder
        raise Warning(f"Não registrada pasta local para {course}")
    
    def load_settings(self):
        try:
            settings_file = self.get_settings_file() # assure right loading if value == ""
            encoding = Decoder.get_encoding(settings_file)
            with open(settings_file, "r", encoding=encoding) as f:
                data = json.load(f)
                self.dict_alias_remote = data.get(self.__remote, {})
                self.dict_alias_folder = data.get(self.__folder, {})
                self.app = AppSettings().from_dict(data.get(self.__appcfg, {}))
                self.colors = Colors().from_dict(data.get(self.__colors, {}))
        except (FileNotFoundError, json.decoder.JSONDecodeError) as _e:
            self.reset()
            self.save_settings()
        return self

    # def check_rootdir(self):
    #     if self.app.get_rootdir() != "":
    #         return self
    #     print(Text().add("Pasta padrão para download de arquivos ").addf("r", "precisa").add(" ser definida."))
    #     here_cwd = os.getcwd()
    #     qxcode = os.path.join(os.path.expanduser("~"), "qxcode")

    #     while True:
    #         print(Text().addf("r", "1").add(" - ").add(here_cwd))
    #         print(Text().addf("r", "2").add(" - ").add(qxcode))
    #         print(Text().addf("r", "3").add(" - ").add("Outra pasta"))
    #         print(Text().add("Default ").addf("r", "1").add(": "), end="")
    #         op = input()
    #         if op == "":
    #             op = "1"
    #         if op == "1":
    #             home_qxcode = here_cwd
    #             break
    #         if op == "2":
    #             home_qxcode = qxcode
    #             break
    #         if op == "3":
    #             print(Text().addf("y", "Navegue até o diretório desejado e execute o tko novamente."))
    #             exit(1)

    #     if not os.path.exists(home_qxcode):
    #         os.makedirs(home_qxcode)
    #     print("Pasta padrão para download de arquivos foi definida em: " + home_qxcode)
    #     print(RawTerminal.centralize("", "-"))
    #     self.app._rootdir = home_qxcode
    #     self.save_settings();
    #     return self
    
    # def check_rep_alias(self, rep_alias: str):
    #     if rep_alias == "__ask":
    #         last = self.app.get_last_rep()
    #         if last != "" and last in self.remote:
    #             rep_alias = last
    #         else:
    #             print("Escolha um dos repositórios para abrir:")
    #             options: Dict[int, str] = {}
    #             for i, alias in enumerate(self.remote, start=1):
    #                 print(Text().addf("r", str(i)).add(f" - {alias}"))
    #                 options[i] = alias
    #             while True:
    #                 try:
    #                     print("Digite o número do repositório desejado: ", end="")
    #                     index = int(input())
    #                     if index in options:
    #                         rep_alias = options[index]
    #                         self.app.set_last_rep(rep_alias)
    #                         self.save_settings()
    #                         break
    #                 except ValueError:
    #                     pass
    #                 print("Digite um número válido")
    #     return rep_alias
    
    def save_settings(self):
        file = self.get_settings_file()
        value = {
            self.__remote: self.dict_alias_remote,
            self.__folder: self.dict_alias_folder,
            self.__appcfg: self.app.to_dict(),
            self.__colors: self.colors.to_dict()
        }
        with open(file, "w", encoding="utf-8") as f:
            json.dump(value, f, indent=4)
        return self

    def __str__(self):
        output = []
        output.append(str(Text("{g}", "Arquivo de configuração:")))
        output.append("- " + self.get_settings_file())
        output.append("")
        output.append(str(Text("{g}", "Repositórios remotos cadastrados:")))
        max_alias = max([len(key) for key in self.dict_alias_remote])
        for key in self.dict_alias_remote:
            output.append("- {} : {}".format(key.ljust(max_alias), self.dict_alias_remote[key]))
        output.append("")
        output.append(str(Text("{g}", "Repositórios locais salvos:")))
        max_alias = max([len(key) for key in self.dict_alias_folder])
        for key in self.dict_alias_folder:
            output.append("- {} : {}".format(key.ljust(max_alias), self.dict_alias_folder[key]))

        app_str = str(self.app)
        return "\n".join(output) + "\n\n" + app_str

        # maxlen = max([len(key) for key in self.remote])
        # for key in self.remote:
        #     prefix = f"- {key.ljust(maxlen)}"
        #     if self.remote[key].file and self.remote[key].url:
        #         output.append(f"{prefix} : dual   : {self.remote[key].url} ; {self.remote[key].file}")
        #     elif self.remote[key].url:
        #         output.append(f"{prefix} : remote : {self.remote[key].url}")
        #     else:
        #         output.append(f"{prefix} : local  : {self.remote[key].file}")
        # return "\n".join(output)
