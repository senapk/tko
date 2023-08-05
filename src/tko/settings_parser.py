import os
import shutil
import configparser
from appdirs import user_data_dir, site_data_dir

class SettingsParser:

#     default_cfg_content = """[REP]
# fup = https://raw.githubusercontent.com/qxcodefup/arcade/master/base/
# ed = https://raw.githubusercontent.com/qxcodeed/arcade/master/base/
# poo = https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/
# """

    def __init__(self):
        self.package_name = "tko"
        self.filename = "settings.cfg"
        self.settings_dir = user_data_dir(self.package_name)
        self.site_data_dir = site_data_dir(self.package_name)
        self.settings_file = os.path.join(self.settings_dir, self.filename)
        self.default_settings_file = os.path.join(self.site_data_dir, self.filename)

    def get_repository(self, disc):
        if not os.path.isfile(self.settings_file):
            self.create_default_settings_file()
        with open(self.settings_file, "r") as f:
            parser = configparser.ConfigParser()
            parser.read(self.settings_file)
            return parser["REP"][disc]

    def create_default_settings_file(self):
        if not os.path.isdir(self.settings_dir):
            os.mkdir(self.settings_dir)
        shutil.copyfile(self.default_settings_file, self.settings_file)

        # with open(self.settings_file, "w") as f:
        #     f.write(SettingsParser.default_cfg_content)

    
    def get_settings_dir(self):
        return self.settings_dir
