from tko.config.check_version import CheckVersion
from tko.installation import InstallationMethod


def test_update_command_uses_managed_installer(monkeypatch) -> None:
    monkeypatch.setattr("tko.config.check_version.installation_method", lambda: InstallationMethod.MANAGED)

    assert CheckVersion.update_command() == "tko self-update"


def test_update_command_preserves_pipx_workflow(monkeypatch) -> None:
    monkeypatch.setattr("tko.config.check_version.installation_method", lambda: InstallationMethod.PIPX)

    assert CheckVersion.update_command() == "pipx upgrade tko"