from pathlib import Path

from tko.config.settings import Settings
from tko.cmds.cmd_build import CmdBuild
from tko.util.param import Param

class Cases:

    @staticmethod
    def run(cases_file: Path, source_readme: Path, source_dir: Path, settings: Settings | None = None) -> bool:
        # Encontra recursivamente arquivos de casos, sem tratar configurações
        # de feedback como testes.
        files: list[Path] = sorted(
            (
                path
                for path in source_dir.rglob("*")
                if path.is_file()
                and path.suffix in {".tio", ".vpl", ".cases", ".toml"}
                and path.name != "feedback.toml"
            ),
            key=lambda path: path.as_posix(),
        )

        effective_settings: Settings = settings if settings is not None else Settings(None)
        command: CmdBuild = CmdBuild(cases_file, [source_readme, *files], Param.Manip(), effective_settings).set_quiet(True)
        succeeded: bool = command.execute()
        if not succeeded:
            cases_file.unlink(missing_ok=True)
        return succeeded
