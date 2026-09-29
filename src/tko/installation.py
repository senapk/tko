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
    aliases: tuple[Path, ...] = ()

    @property
    def python(self) -> Path:
        return self.venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    @property
    def executable(self) -> Path:
        return self.venv / ("Scripts/tko.exe" if sys.platform == "win32" else "bin/tko")

    @classmethod
    def from_executable(cls, executable: Path) -> ManagedInstallation | None:
        resolved: Path = executable.resolve()
        venv_parent: Path = resolved.parent
        if venv_parent.name not in {"bin", "Scripts"} or venv_parent.parent.name != "venv":
            return None
        root: Path = resolved.parent.parent.parent
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
        aliases_value: object = data.get("aliases", [])
        aliases: tuple[Path, ...] = (
            tuple(Path(alias) for alias in aliases_value if isinstance(alias, str))
            if isinstance(aliases_value, list)
            else ()
        )
        return cls(root, root / "venv", metadata, Path(launcher), aliases)


def installation_method(executable: Path | None = None) -> InstallationMethod:
    current: Path = executable or Path(sys.executable)
    if ManagedInstallation.from_executable(current) is not None:
        return InstallationMethod.MANAGED
    if "pipx" in current.resolve().parts:
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
    launchers: tuple[Path, ...] = (installation.launcher, *installation.aliases)
    for launcher in launchers:
        if not launcher.exists():
            continue
        if launcher == installation.launcher and launcher.name == "tko" and not installation.aliases:
            binaries: tuple[str, ...] = ("tko",)
        elif launcher.name == "tko":
            binaries = ("tko", "soin")
        elif launcher.name == "tkm":
            binaries = ("tkm", "tejo")
        elif launcher.name in {"tejo", "koa"}:
            binaries = ("tejo",)
        elif launcher.name == "soin":
            binaries = ("soin",)
        else:
            binaries = ("tko",)
        bin_folder: str = "Scripts" if sys.platform == "win32" else "bin"
        expected_targets: tuple[str, ...] = tuple(
            str(installation.venv / bin_folder / (f"{binary}.exe" if sys.platform == "win32" else binary))
            for binary in binaries
        )
        launcher_contents: str = launcher.read_text(encoding="utf-8")
        if not any(target in launcher_contents for target in expected_targets):
            raise ValueError("Managed TKO launcher does not match its virtual environment")
    for launcher in launchers:
        launcher.unlink(missing_ok=True)
    shutil.rmtree(installation.root)
