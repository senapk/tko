import os

from tko.settings.settings import Settings
from tko.util.consts import DiffMode

class ConfigParams:
    def __init__(self):
        self.side: bool = False
        self.down: bool = False
        self.lang: str | None = None
        self.ask: bool = False
        self.root: str | None = None
        self.editor: str | None = None
        self.hud: str | None = None
        self.borders: str | None = None

    def __str__(self):
        return f"side: {self.side}, down: {self.down}, lang: {self.lang}, ask: {self.ask}, root: {self.root}, editor: {self.editor}"

class CmdConfig:
        
    @staticmethod
    def execute(settings: Settings, param: ConfigParams):
        action = False

        if param.borders is not None:
            action = True
            settings.app.set_borders(param.borders == "1")
            print("Borders now is: " + str("True" if param.borders == "1" else "False"))
        if param.side:
            action = True
            settings.app.set_diff_mode(DiffMode.SIDE)
            print("Diff mode now is: SIDE_BY_SIDE")
        if param.down:
            action = True
            settings.app.set_diff_mode(DiffMode.DOWN)
            print("Diff mode now is: UP_DOWN")
        if param.lang:
            action = True
            settings.app._lang_default = param.lang
            print("Default language extension now is:", param.lang)
        if param.ask:
            action = True
            settings.app._lang_default = ""
            print("Language extension will be asked always.")

        if param.root:
            action = True
            path = os.path.abspath(param.root)
            settings.app._rootdir = path
            print("Root directory now is: " + path)
        
        if param.editor:
            action = True
            settings.app._editor = param.editor
            print(f"Novo comando para abrir arquivos de código: {param.editor}")

        if not action:
            action = True
            print(settings.get_settings_file())
            print("Rootdir: {}".format(settings.app.get_rootdir()))
            print("Diff   : {}".format(str(settings.app.get_diff_mode())))
            print("Editor : {}".format(settings.app.get_editor()))
            print("Bordas : {}".format(settings.app.has_borders()))
            print("Images : {}".format(settings.app.has_images()))
            value = settings.app.get_lang_default()
            print("Linguagem default: {}".format("Não definido" if value == "" else value))

        settings.save_settings()