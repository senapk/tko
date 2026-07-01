from tko.feno.github_url_structure import GitHubUrlStructure
from tko.i18n import Msg
from tko.util.rt import RT


import tomllib
from pathlib import Path
from tko.util.console import Console


_FENO_GITHUB_CFG_NOT_SET = Msg.parse(
    pt="fail: arquivo {filename} não definido",
    en="fail: {filename} file not set",
)


class GithubCfg:
    FILENAME = "remote.toml"
    def __init__(self, target: Path, make_remote: bool):
        self.target = target
        self.remote: GitHubUrlStructure | None = None
        self.cfg_path: Path | None = None
        if make_remote:
            self.__load_cfg_path(target)
            self.__parse_cfg()
            if self.cfg_path is None:
                Console.print(RT(str(_FENO_GITHUB_CFG_NOT_SET).format(filename=self.FILENAME), "r"))

    def cfg_exists(self):
        return self.cfg_path is not None

    def get_cfg_path(self) -> Path:
        if self.cfg_path is None:
            raise Exception("cfg_path not set")
        return self.cfg_path.resolve()

    def calc_link_for_local_file(self):
        root_dir = self.get_cfg_path().parent
        target_file = self.target.resolve()
        self.target
        if not target_file.is_relative_to(root_dir):
            raise Exception(f"File not match with {self.FILENAME}")
        if self.remote is None:
            raise Exception("remote not set")
        return self.remote.with_relative_path(str(target_file.relative_to(root_dir)), "blob")

    def __parse_cfg(self):
        if self.cfg_path is None:
            return
        with open(self.get_cfg_path(), "rb") as f:
            config = tomllib.load(f)

        self.remote = GitHubUrlStructure(
            user=config["user"],
            repo=config["repository"],
            branch=config["branch"],
        )

    def __load_cfg_path(self, target: Path) -> None:
        for path in [target.resolve(), *target.resolve().parents]:
            cfg_path = path / self.FILENAME

            if cfg_path.is_file():
                self.cfg_path = cfg_path
                return
