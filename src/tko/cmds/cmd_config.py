import os

from tko.settings.settings import Settings

class ConfigParams:
    def __init__(self):
        self.ascii = False
        self.unicode = False
        self.mono = False
        self.color = False
        self.side = False
        self.down = False
        self.lang = None
        self.ask = False
        self.root = None
        self.editor = None

    def __str__(self):
        return f"ascii: {self.ascii}, unicode: {self.unicode}, mono: {self.mono}, color: {self.color}, side: {self.side}, down: {self.down}, lang: {self.lang}, ask: {self.ask}, root: {self.root}, editor: {self.editor}"

class CmdConfig:
        
    @staticmethod
    def execute(settings: Settings, param: ConfigParams):
        action = False

        if param.ascii:
            action = True
            settings.app.set_ascii(True)
            print("Encoding mode now is: ASCII")
        if param.unicode:
            action = True
            settings.app.set_ascii(False)
            print("Encoding mode now is: UNICODE")
        if param.mono:
            action = True
            settings.app.set_colored(False)
            print("Color mode now is: MONOCHROMATIC")
        if param.color:
            action = True
            settings.app.set_colored(True)
            print("Color mode now is: COLORED")
        if param.side:
            action = True
            settings.app._diff_mode = "side"
            print("Diff mode now is: SIDE_BY_SIDE")
        if param.down:
            action = True
            settings.app._diff_mode = "down"
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
            print("Diff mode: {}".format("DOWN" if settings.app.get_diff_mode() else "SIDE"))
            print("Encoding mode: {}".format("ASCII" if settings.app.is_ascii() else "UNICODE"))
            print("Color mode: {}".format("MONOCHROMATIC" if not settings.app.is_colored() else "COLORED"))
            value = settings.app._lang_default
            print("Default language extension: {}".format("Always ask" if value == "" else value))

        settings.save_settings()