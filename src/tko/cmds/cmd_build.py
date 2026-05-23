import logging
from pathlib import Path

from tko.util.param import Param
from tko.run.wdir import Wdir
from tko.run.writer import Writer
from tko.config.settings import Settings
from tko.i18n import Msg, t


logger = logging.getLogger(__name__)

_CMD_BUILD_EXECUTE_FAILED = Msg(
    pt="Falha ao executar o build para {target}",
    en="Failed to execute build for {target}",
)

class CmdBuild:

    def __init__(self, target_out: Path, source_list: list[Path], param: Param.Manip, settings: Settings):
        self.target_out = target_out
        self.source_list = source_list
        self.param = param
        self.settings = settings
        self.quiet = False

    def set_quiet(self, value: bool):
        self.quiet = value
        return self

    def execute(self):
        try:
            wdir = Wdir(self.settings)
            wdir.source_list = self.source_list
            wdir.build_unit_list()
            wdir.manipulate(self.param)
            Writer.save_target(self.target_out, wdir.unit_list, quiet=self.quiet)
        except FileNotFoundError:
            logger.exception(t(_CMD_BUILD_EXECUTE_FAILED, target=self.target_out))
            return False
        return True
