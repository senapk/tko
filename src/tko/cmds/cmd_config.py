# from typing import override

from tko.config.settings import Settings
from tko.enums.diff_mode import DiffMode
from tko.i18n import MsgKey, t

class ConfigParams:
    def __init__(self):
        self.side: bool = False
        self.down: bool = False
        self.images: str | None = None
        self.editor: str | None = None
        self.borders: str | None = None
        self.timeout: int | None = None

    # @override
    def __str__(self) -> str: 
        return f"side: {self.side}, down: {self.down}, timeout: {self.timeout}, editor: {self.editor}, borders: {self.borders}, images: {self.images}"

class CmdConfig:
        
    @staticmethod
    def execute(settings: Settings, param: ConfigParams):
        action = False

        if param.borders is not None:
            action = True
            settings.app.use_borders = True
            status = "True" if param.borders == "1" else "False"
            print(t(MsgKey.CONFIG_BORDERS_STATUS, status=status))
        if param.images is not None:
            action = True
            settings.app.use_images = param.images == "1"
            status = "True" if param.images == "1" else "False"
            print(t(MsgKey.CONFIG_IMAGES_STATUS, status=status))
            
        if param.side:
            action = True
            settings.app.diff_mode = DiffMode.SIDE
            print(t(MsgKey.CONFIG_DIFF_MODE_SIDE))
        if param.down:
            action = True
            settings.app.diff_mode = DiffMode.DOWN
            print(t(MsgKey.CONFIG_DIFF_MODE_DOWN))
        # if param.lang:
        #     action = True
        #     settings.app._lang_default = param.lang
        #     print("Default language extension now is:", param.lang)
        # if param.ask:
        #     action = True
        #     settings.app._lang_default = ""
        #     print("Language extension will asked be always.")
        
        if param.editor:
            action = True
            settings.app.editor = param.editor
            print(t(MsgKey.CONFIG_EDITOR_CHANGED, editor=param.editor))

        if param.timeout is not None:
            action = True
            settings.app.timeout = param.timeout
            print(t(MsgKey.CONFIG_TIMEOUT_CHANGED, timeout=param.timeout))

        if not action:
            print(str(settings))

        settings.save_settings()