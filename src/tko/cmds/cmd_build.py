import logging
from pathlib import Path

from tko.util.param import Param
from tko.run.wdir import Wdir
from tko.run.writer import Writer
from tko.config.settings import Settings


logger = logging.getLogger(__name__)

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
            wdir = Wdir(self.settings).set_sources(self.source_list).build()
            wdir.manipulate(self.param)
            Writer.save_target(self.target_out, wdir.get_unit_list(), quiet=self.quiet)
        except FileNotFoundError:
            logger.exception("Falha ao executar o build para %s", self.target_out)
            return False
        return True
