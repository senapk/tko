from tko.util.param import Param
from tko.run.wdir import Wdir
from tko.run.writer import Writer

class CmdBuild:

    def __init__(self, target_out: str, source_list: list[str], param: Param.Manip):
        self.target_out = target_out
        self.source_list = source_list
        self.param = param
        self.quiet = False


    def set_quiet(self, value: bool):
        self.quiet = value
        return self

    def execute(self):
        try:
            wdir = Wdir().set_sources(self.source_list).build()
            wdir.manipulate(self.param)
            Writer.save_target(self.target_out, wdir.get_unit_list(), quiet=self.quiet)
        except FileNotFoundError as e:
            print(str(e))
            return False
        return True
