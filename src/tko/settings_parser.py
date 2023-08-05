import os
import configparser
from appdirs import user_data_dir
import appdirs


class SettingsParser:
    package_name = "tko"
    file_name = "settings.cfg"

    settings_file = os.path.join(user_data_dir(package_name), file_name)

    default_cfg_content = """[REP]
fup = https://raw.githubusercontent.com/qxcodefup/arcade/master/base/
ed = https://raw.githubusercontent.com/qxcodeed/arcade/master/base/
poo = https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/
"""

    @staticmethod
    def get_repository(disc):
        if not os.path.isfile(SettingsParser.settings_file):
            SettingsParser.create_default_settings_file()
        with open(SettingsParser.settings_file, "r") as f:
            parser = configparser.ConfigParser()
            parser.read(SettingsParser.settings_file)
            return parser["REP"][disc]

    # @staticmethod
    # def create_default_settings_file():
    #     if not os.path.isdir(user_data_dir(SettingsParser.package_name)):
    #         os.mkdir(user_data_dir(SettingsParser.package_name))
    #     with open(SettingsParser.settings_file, "w") as f:
    #         f.write(SettingsParser.default_cfg_content)
