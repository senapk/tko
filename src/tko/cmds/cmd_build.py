from typing import List
from ..util.param import Param
from ..run.wdir import Wdir
from ..run.writer import Writer


class CmdBuild:

    def __init__(self, target_out: str, source_list: List[str], param: Param.Manip, to_force: bool):
        self.target_out = target_out
        self.source_list = source_list
        self.param = param
        self.to_force = to_force

    def execute(self):
        try:
            wdir = Wdir().set_sources(self.source_list).build()
            wdir.manipulate(self.param)
            Writer.save_target(self.target_out, wdir.get_unit_list(), self.to_force)
        except FileNotFoundError as e:
            print(str(e))
            return False
        return True
