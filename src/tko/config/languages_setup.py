import logging

logger = logging.getLogger(__name__)


class LanguageSetup:
    def __init__(self, build_cmd: list[str], run_cmd: list[str], draft: str):
        self.build_cmd: list[str] = build_cmd
        self.run_cmd: list[str] = run_cmd
        self.draft: str = draft

    def to_dict(self):
        return self.__dict__

    def from_dict(self, attr_dict: dict[str, str | list[str]]):
        build_cmd = attr_dict.get("build_cmd", [])
        if isinstance(build_cmd, list):
            self.build_cmd = build_cmd
        run_cmd = attr_dict.get("run_cmd", [])
        if isinstance(run_cmd, list):
            self.run_cmd = run_cmd
        draft = attr_dict.get("draft", "")
        if isinstance(draft, str):
            self.draft = draft
        return self
