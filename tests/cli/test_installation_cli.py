from pathlib import Path
from types import SimpleNamespace
from typing import Any

import typer
from pytest import MonkeyPatch
from typer.testing import CliRunner

import tko.cli.cli_main as cli_main
from tko.cli.cli_main import register_main_commands
from tko.installation import InstallationMethod, ManagedInstallation


def _managed_installation(tmp_path: Path) -> ManagedInstallation:
    root: Path = tmp_path / "tko"
    venv: Path = root / "venv"
    launcher: Path = tmp_path / "bin" / "tko"
    metadata: Path = root / "install.toml"
    return ManagedInstallation(root, venv, metadata, launcher)


def _app() -> typer.Typer:
    app = typer.Typer()
    register_main_commands(app)
    return app


def test_self_update_uses_managed_installation(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    installation = _managed_installation(tmp_path)
    captured: dict[str, ManagedInstallation] = {}

    def find_installation(_executable: Path) -> ManagedInstallation:
        return installation

    def run_update(value: ManagedInstallation) -> None:
        captured["installation"] = value

    monkeypatch.setattr("tko.installation.ManagedInstallation.from_executable", find_installation)
    monkeypatch.setattr("tko.installation.run_self_update", run_update)
    result = CliRunner().invoke(_app(), ["self-update"])

    assert result.exit_code == 0
    assert captured["installation"] == installation
    assert "TKO atualizado." in result.output


def test_self_update_preserves_pipx_installation(monkeypatch: MonkeyPatch) -> None:
    def missing_installation(_executable: Path) -> None:
        return None

    monkeypatch.setattr("tko.installation.ManagedInstallation.from_executable", missing_installation)
    monkeypatch.setattr("tko.installation.installation_method", lambda: InstallationMethod.PIPX)
    result = CliRunner().invoke(_app(), ["self-update"])

    assert result.exit_code == 1
    assert "pipx upgrade tko" in result.output


def test_uninstall_managed_installation_with_yes(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    installation = _managed_installation(tmp_path)
    captured: dict[str, ManagedInstallation] = {}

    def find_installation(_executable: Path) -> ManagedInstallation:
        return installation

    def remove(value: ManagedInstallation) -> None:
        captured["installation"] = value

    monkeypatch.setattr("tko.installation.ManagedInstallation.from_executable", find_installation)
    monkeypatch.setattr("tko.installation.remove_managed_installation", remove)
    result = CliRunner().invoke(_app(), ["uninstall", "--yes"])

    assert result.exit_code == 0
    assert captured["installation"] == installation
    assert "TKO removido." in result.output


def test_uninstall_preserves_pipx_installation(monkeypatch: MonkeyPatch) -> None:
    def missing_installation(_executable: Path) -> None:
        return None

    def pipx_method() -> InstallationMethod:
        return InstallationMethod.PIPX

    monkeypatch.setattr("tko.installation.ManagedInstallation.from_executable", missing_installation)
    monkeypatch.setattr("tko.installation.installation_method", pipx_method)
    result = CliRunner().invoke(_app(), ["uninstall", "--yes"])

    assert result.exit_code == 1
    assert "pipx uninstall tko" in result.output