# from typing import override

from tko.settings.settings import Settings
from tko.enums.diff_mode import DiffMode

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
            settings.app.set_use_borders(param.borders == "1")
            print("Borders now is: " + str("True" if param.borders == "1" else "False"))
        if param.images is not None:
            action = True
            settings.app.set_use_images(param.images == "1")
            print("Images now is: " + str("True" if param.images == "1" else "False"))
            
        if param.side:
            action = True
            settings.app.set_diff_mode(DiffMode.SIDE)
            print("Diff mode now is: SIDE_BY_SIDE")
        if param.down:
            action = True
            settings.app.set_diff_mode(DiffMode.DOWN)
            print("Diff mode now is: UP_DOWN")
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
            print(f"Novo comando para abrir arquivos de código: {param.editor}")

        if param.timeout is not None:
            action = True
            settings.app.set_timeout(param.timeout)
            print(f"Novo timeout: {param.timeout}")

        if not action:
            print(str(settings))

        settings.save_settings()