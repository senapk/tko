# from typing import override

from tko.config.settings import Settings
from tko.enums.diff_mode import DiffMode
from tko.i18n import Msg, t


_CONFIG_IMAGES_STATUS = Msg(
    pt="Imagens agora está: {status}",
    en="Images now is: {status}",
)
_CONFIG_DIFF_MODE_SIDE = Msg(
    pt="Modo de diferença agora é: LADO_A_LADO",
    en="Diff mode now is: SIDE_BY_SIDE",
)
_CONFIG_DIFF_MODE_DOWN = Msg(
    pt="Modo de diferença agora é: CIMA_BAIXO",
    en="Diff mode now is: UP_DOWN",
)
_CONFIG_EDITOR_CHANGED = Msg(
    pt="Novo comando para abrir arquivos de código: {editor}",
    en="New command to open source files: {editor}",
)
_CONFIG_TIMEOUT_CHANGED = Msg(
    pt="Novo timeout: {timeout}",
    en="New timeout: {timeout}",
)

class ConfigParams:
    def __init__(self):
        self.side: bool = False
        self.down: bool = False
        self.images: str | None = None
        self.editor: str | None = None
        self.timeout: int | None = None

    # @override
    def __str__(self) -> str: 
        return f"side: {self.side}, down: {self.down}, timeout: {self.timeout}, editor: {self.editor}, images: {self.images}"

class CmdConfig:
        
    @staticmethod
    def execute(settings: Settings, param: ConfigParams):
        action = False

        if param.images is not None:
            action = True
            settings.app.use_images = param.images == "1"
            status = "True" if param.images == "1" else "False"
            print(t(_CONFIG_IMAGES_STATUS, status=status))
            
        if param.side:
            action = True
            settings.app.diff_mode = DiffMode.SIDE
            print(t(_CONFIG_DIFF_MODE_SIDE))
        if param.down:
            action = True
            settings.app.diff_mode = DiffMode.DOWN
            print(t(_CONFIG_DIFF_MODE_DOWN))
        if param.editor:
            action = True
            settings.app.editor = param.editor
            print(t(_CONFIG_EDITOR_CHANGED, editor=param.editor))

        if param.timeout is not None:
            action = True
            settings.app.timeout = param.timeout
            print(t(_CONFIG_TIMEOUT_CHANGED, timeout=param.timeout))

        if not action:
            print(str(settings))

        settings.save_settings()