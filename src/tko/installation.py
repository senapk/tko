"""Detect and maintain the optional script-managed TKO installation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib


class InstallationMethod(Enum):
    MANAGED = "managed"
    PIPX = "pipx"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class ManagedInstallation:
    root: Path
    venv: Path
    metadata: Path
    launcher: Path

    @property
    def python(self) -> Path:
        return self.venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    @property
    def executable(self) -> Path:
        return self.venv / ("Scripts/tko.exe" if sys.platform == "win32" else "bin/tko")

    @classmethod
    def from_executable(cls, executable: Path) -> ManagedInstallation | None:
        # Keep the virtualenv path intact: on Unix, venv/bin/python is usually
        # a symlink to the system interpreter, and resolve() loses the venv.
        absolute: Path = executable.absolute()
        venv_parent: Path = absolute.parent
        if venv_parent.name not in {"bin", "Scripts"} or venv_parent.parent.name != "venv":
            return None
        root: Path = absolute.parent.parent.parent
        metadata: Path = root / "install.toml"
        if not metadata.is_file():
            return None
        try:
            data: object = tomllib.loads(metadata.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            return None
        if not isinstance(data, dict) or data.get("method") != InstallationMethod.MANAGED.value:
            return None
        launcher: object = data.get("launcher")
        if not isinstance(launcher, str) or not launcher:
            return None
        return cls(root, root / "venv", metadata, Path(launcher))


def installation_method(executable: Path | None = None) -> InstallationMethod:
    current: Path = executable or Path(sys.executable)
    if ManagedInstallation.from_executable(current) is not None:
        return InstallationMethod.MANAGED
    if "pipx" in current.absolute().parts:
        return InstallationMethod.PIPX
    return InstallationMethod.OTHER


def self_update_command(installation: ManagedInstallation) -> list[str]:
    return [str(installation.python), "-m", "pip", "install", "--upgrade", "tko"]


def run_self_update(installation: ManagedInstallation) -> None:
    subprocess.run(self_update_command(installation), check=True)


def remove_managed_installation(installation: ManagedInstallation) -> None:
    if (
        installation.root.name != "tko"
        or installation.venv != installation.root / "venv"
        or installation.metadata != installation.root / "install.toml"
    ):
        raise ValueError("Invalid managed TKO installation")
    if installation.launcher.exists():
        bin_folder: str = "Scripts" if sys.platform == "win32" else "bin"
        binary: str = "tko.exe" if sys.platform == "win32" else "tko"
        expected_target: str = str(installation.venv / bin_folder / binary)
        launcher_contents: str = installation.launcher.read_text(encoding="utf-8")
        if expected_target not in launcher_contents:
            raise ValueError("Managed TKO launcher does not match its virtual environment")
        installation.launcher.unlink()
    shutil.rmtree(installation.root)
