from pathlib import Path
import os

import pytest

from tko.installation import (
    InstallationMethod,
    ManagedInstallation,
    installation_method,
    remove_managed_installation,
    self_update_command,
)


def _managed_installation(root: Path) -> ManagedInstallation:
    executable_name: str = "python.exe" if os.name == "nt" else "python"
    bin_dir: str = "Scripts" if os.name == "nt" else "bin"
    python: Path = root / "venv" / bin_dir / executable_name
    python.parent.mkdir(parents=True)
    python.touch()
    launcher: Path = root.parent.parent / "bin" / "tko"
    launcher.parent.mkdir(parents=True)
    executable: Path = root / "venv" / bin_dir / ("tko.exe" if os.name == "nt" else "tko")
    launcher.write_text(f'#!/bin/sh\nexec "{executable}" "$@"\n', encoding="utf-8")
    (root / "install.toml").write_text(
        f'method = "managed"\nlauncher = "{launcher}"\n', encoding="utf-8"
    )
    installation = ManagedInstallation.from_executable(python)
    assert installation is not None
    return installation


def test_managed_installation_is_detected_and_updated_with_its_venv(tmp_path: Path) -> None:
    installation = _managed_installation(tmp_path / ".local" / "share" / "tko")

    assert installation_method(installation.python) == InstallationMethod.MANAGED
    assert self_update_command(installation) == [
        str(installation.python), "-m", "pip", "install", "--upgrade", "tko",
    ]


def test_pipx_executable_is_detected_without_metadata(tmp_path: Path) -> None:
    executable: Path = tmp_path / "pipx" / "venvs" / "tko" / "bin" / "python"
    executable.parent.mkdir(parents=True)
    executable.touch()

    assert installation_method(executable) == InstallationMethod.PIPX


def test_removing_managed_installation_keeps_other_files(tmp_path: Path) -> None:
    installation = _managed_installation(tmp_path / ".local" / "share" / "tko")
    unrelated: Path = tmp_path / ".local" / "share" / "other.txt"
    unrelated.write_text("keep", encoding="utf-8")

    remove_managed_installation(installation)

    assert not installation.root.exists()
    assert not installation.launcher.exists()
    assert unrelated.read_text(encoding="utf-8") == "keep"


def test_removing_managed_installation_refuses_unrelated_launcher(tmp_path: Path) -> None:
    installation = _managed_installation(tmp_path / ".local" / "share" / "tko")
    installation.launcher.write_text("external launcher\n", encoding="utf-8")

    with pytest.raises(ValueError, match="does not match"):
        remove_managed_installation(installation)

    assert installation.root.exists()
    assert installation.launcher.exists()