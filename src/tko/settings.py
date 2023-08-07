import os
import configparser
from appdirs import user_data_dir
from typing import Optional


class SettingsParser:

    default_cfg_content = """[REP]
fup = https://raw.githubusercontent.com/qxcodefup/arcade/master/base/
ed = https://raw.githubusercontent.com/qxcodeed/arcade/master/base/
poo = https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/

[VISUAL]
ascii = False
"""

    __settings_file: Optional[str] = None

    def __init__(self):
        self.package_name = "tko"
        self.filename = "settings.cfg"
        if SettingsParser.__settings_file is None:
            self.settings_file = os.path.join(user_data_dir(self.package_name), self.filename)
        else:
            self.settings_file = os.path.abspath(SettingsParser.__settings_file)

    def get_repository(self, disc):
        if not os.path.isfile(self.settings_file):
            self.create_default_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        return parser["REP"][disc]

    def get_settings_dir(self):
        return os.path.dirname(self.settings_file)

    def create_default_settings_file(self):
        if not os.path.isdir(self.get_settings_dir()):
            os.makedirs(self.get_settings_dir(), exist_ok=True)
        with open(self.settings_file, "w") as f:
            f.write(self.default_cfg_content)

    def check_settings_file(self):
        if not os.path.isfile(self.settings_file):
            self.create_default_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        if "VISUAL" not in parser or "REP" not in parser:
            self.create_default_settings_file()

    def get_settings_file(self):
        self.check_settings_file()
        return self.settings_file
    
    def set_settings_file(self, path):
        path = os.path.abspath(path)
        SettingsParser.__settings_file = path
        self.settings_file = path

    def get_ascii(self) -> bool:
        self.check_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        return parser["VISUAL"]["ascii"] == "True"
    
    def toggle_ascii(self):
        self.check_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        parser["VISUAL"]["ascii"] = str(not self.get_ascii())
        with open(self.settings_file, "w") as f:
            parser.write(f)

