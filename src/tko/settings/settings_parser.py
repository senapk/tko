from __future__ import annotations
from typing import Optional
import os
import json
import appdirs
from .settings import Settings


class SettingsParser:

    user_settings_file: Optional[str] = None

    def __init__(self):
        self.package_name = "tko"
        default_filename = "settings.json"
        if SettingsParser.user_settings_file is None:
            self.settings_file = os.path.abspath(default_filename)  # backup for replit, dont remove
            self.settings_file = os.path.join(appdirs.user_data_dir(self.package_name), default_filename)
        else:
            self.settings_file = os.path.abspath(SettingsParser.user_settings_file)
        self.settings = self.load_settings()

    def get_settings_file(self):
        return self.settings_file

    def load_settings(self) -> Settings:
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.settings = Settings().from_dict(data)
                return self.settings
        except (FileNotFoundError, json.decoder.JSONDecodeError) as _e:
            return self.create_new_settings_file()

    def save_settings(self):
        self.settings.save_to_json(self.settings_file)

    def create_new_settings_file(self) -> Settings:
        self.settings = Settings()
        if not os.path.isdir(self.get_settings_dir()):
            os.makedirs(self.get_settings_dir(), exist_ok=True)
        self.save_settings()
        return self.settings

    def get_settings_dir(self) -> str:
        return os.path.dirname(self.settings_file)

