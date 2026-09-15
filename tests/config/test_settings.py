from pathlib import Path
import tomllib

from tko.config.settings import Settings


def test_global_settings_migrate_from_yaml_to_toml(tmp_path: Path) -> None:
    legacy: Path = tmp_path / "settings.yaml"
    legacy.write_text(
        "gitrepos:\n  custom: https://example.com/index.md\nappcfg:\n  theme: tko-light\n  timeout: 9\n",
        encoding="utf-8",
    )

    settings: Settings = Settings(tmp_path).load_settings()

    current: Path = tmp_path / "settings.toml"
    assert settings.app.theme == "tko-light"
    assert settings.app.timeout == 9
    assert settings.get_alias_git("custom") == "https://example.com/index.md"
    assert not legacy.exists()
    assert (tmp_path / "settings.yaml.backup").is_file()
    data: dict[str, object] = tomllib.loads(current.read_text(encoding="utf-8"))
    assert data["gitrepos"] == {"custom": "https://example.com/index.md"}
    assert data["appcfg"] == settings.app.to_dict()