import os
import configparser
import appdirs
from typing import Optional


class SettingsParser:

    default_cfg_content = """[REP]
fup = https://raw.githubusercontent.com/qxcodefup/arcade/master/base/
ed = https://raw.githubusercontent.com/qxcodeed/arcade/master/base/
poo = https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/

[LOCAL]
; use "lang = ask" to ask for language every time
lang = ask

[VISUAL]
ascii = False
color = True
hdiff = True
hdiffmin = 60
"""

    __settings_file: Optional[str] = None

    def __init__(self):
        self.package_name = "tko"
        self.filename = "settings.cfg"
        if SettingsParser.__settings_file is None:
            self.settings_file = "./tko.cfg"
            self.settings_file = os.path.join(appdirs.user_data_dir(self.package_name), self.filename)
        else:
            self.settings_file = os.path.abspath(SettingsParser.__settings_file)

    def get_repository(self, disc) -> Optional[str]:
        if not os.path.isfile(self.settings_file):
            self.create_default_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)

        if disc not in parser["REP"]:
            return None

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
        if "VISUAL" not in parser or "REP" not in parser or "LOCAL" not in parser:
            self.create_default_settings_file()

        parser.read(self.settings_file)  
        update = False

        if "lang" not in parser["LOCAL"]:
            parser["LOCAL"]["lang"] = "ask"
            update = True

        if "ascii" not in parser["VISUAL"]:
            parser["VISUAL"]["ascii"] = "False"
            update = True

        if "color" not in parser["VISUAL"]:
            parser["VISUAL"]["color"] = "True"
            update = True

        if "hdiff" not in parser["VISUAL"]:
            parser["VISUAL"]["hdiff"] = "True"
            update = True
        
        if "hdiffmin" not in parser["VISUAL"]:
            parser["VISUAL"]["hdiffmin"] = "60"
            update = True

        if update:
            with open(self.settings_file, "w") as f:
                parser.write(f)


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
    
    def set_ascii(self, value):
        self.check_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        parser["VISUAL"]["ascii"] = str(value)
        with open(self.settings_file, "w") as f:
            parser.write(f)

    def get_color(self) -> bool:
        self.check_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        return parser["VISUAL"]["color"] == "True"
    
    def set_color(self, value: bool):
        self.check_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        parser["VISUAL"]["color"] = str(value)
        with open(self.settings_file, "w") as f:
            parser.write(f)

    def get_hdiff(self) -> bool:
        self.check_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        return parser["VISUAL"]["hdiff"] == "True"
    
    def set_hdiff(self, value: bool):
        self.check_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        parser["VISUAL"]["hdiff"] = str(value)
        with open(self.settings_file, "w") as f:
            parser.write(f)

    def get_hdiffmin(self) -> int:
        self.check_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        return int(parser["VISUAL"]["hdiffmin"])
    
    def set_language(self, lang):
        self.check_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        parser["LOCAL"]["lang"] = lang
        with open(self.settings_file, "w") as f:
            parser.write(f)
    
    def get_language(self):
        self.check_settings_file()
        parser = configparser.ConfigParser()
        parser.read(self.settings_file)
        return parser["LOCAL"]["lang"]
    
    def __str__(self):
        output = ""

        output += "Settings File: " + self.get_settings_file() + "\n"
        output += "Default  Lang: " + self.get_language() + "\n"
        output += "Diff     Mode: " + ("SIDE_BY_SIDE" if self.get_hdiff() else "UP_DOWN") + "\n"
        output += "Color    Mode: " + ("COLORED" if self.get_color() else "MONO") + "\n"
        output += "Encoding Mode: " + ("ASCII" if self.get_ascii() else "UNICODE") + "\n"

        return output
