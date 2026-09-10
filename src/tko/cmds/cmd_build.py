from loguru import logger
from pathlib import Path

from tko.util.param import Param
from tko.run.wdir import Wdir
from tko.run.writer import Writer
from tko.config.settings import Settings
from tko.i18n import Msg
from tko.util.pattern_loader import DEFAULT_DIRECTORY_PATTERN
import sys




_CMD_BUILD_EXECUTE_FAILED = Msg.parse(
    pt="Falha ao executar o build para {target}",
    en="Failed to execute build for {target}",
)

class CmdBuild:

    def __init__(
        self,
        target_out: Path | None,
        source_list: list[Path],
        param: Param.Manip,
        settings: Settings,
        read_pattern: str = DEFAULT_DIRECTORY_PATTERN,
        write_pattern: str = DEFAULT_DIRECTORY_PATTERN,
    ):
        self.target_out = target_out
        self.source_list = source_list
        self.param = param
        self.settings = settings
        self.read_pattern = read_pattern
        self.write_pattern = write_pattern
        self.quiet = False

    def set_quiet(self, value: bool):
        self.quiet = value
        return self

    def execute(self):
        try:
            wdir = Wdir(self.settings)
            wdir.source_list = self.source_list
            wdir.build_unit_list(self.read_pattern)
            wdir.manipulate(self.param)
            if self.target_out is None:
                sys.stdout.write(Writer.render_toml(wdir.unit_list))
            else:
                Writer.save_target(self.target_out, wdir.unit_list, quiet=self.quiet, pattern=self.write_pattern)
        except FileNotFoundError:
            logger.exception(_CMD_BUILD_EXECUTE_FAILED.t().format(target=self.target_out))
            return False
        return True
