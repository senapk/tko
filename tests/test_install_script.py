import os
from pathlib import Path
import subprocess


def _fake_python(path: Path) -> None:
    path.write_text(
        "#!/usr/bin/env sh\n"
        "if [ \"$1\" = \"-m\" ] && [ \"$2\" = \"venv\" ]; then\n"
        "  mkdir -p \"$3/bin\"\n"
        "  printf '#!/usr/bin/env sh\\nexit 0\\n' > \"$3/bin/python\"\n"
        "  printf '#!/usr/bin/env sh\\nexit 0\\n' > \"$3/bin/tko\"\n"
        "  chmod 755 \"$3/bin/python\" \"$3/bin/tko\"\n"
        "fi\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_install_script_creates_managed_venv_launcher_and_metadata(tmp_path: Path) -> None:
    fake_bin: Path = tmp_path / "bin"
    fake_bin.mkdir()
    _fake_python(fake_bin / "python3")
    home: Path = tmp_path / "home"
    environment: dict[str, str] = {
        **os.environ,
        "HOME": str(home),
        "PATH": f"{fake_bin}:/usr/bin:/bin",
    }

    result = subprocess.run(
        ["/usr/bin/env", "bash", "install.sh"],
        cwd=Path(__file__).parents[1],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    root: Path = home / ".local" / "share" / "tko"
    launcher: Path = home / ".local" / "bin" / "tko"
    assert result.returncode == 0, result.stderr
    assert (root / "venv" / "bin" / "tko").is_file()
    assert 'method = "managed"' in (root / "install.toml").read_text(encoding="utf-8")
    assert str(launcher) in (root / "install.toml").read_text(encoding="utf-8")
    assert str(root / "venv" / "bin" / "tko") in launcher.read_text(encoding="utf-8")


def test_install_script_does_not_replace_existing_launcher(tmp_path: Path) -> None:
    home: Path = tmp_path / "home"
    launcher: Path = home / ".local" / "bin" / "tko"
    launcher.parent.mkdir(parents=True)
    launcher.write_text("existing launcher\n", encoding="utf-8")

    result = subprocess.run(
        ["/usr/bin/env", "bash", "install.sh"],
        cwd=Path(__file__).parents[1],
        env={**os.environ, "HOME": str(home)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert launcher.read_text(encoding="utf-8") == "existing launcher\n"
    assert "não será sobrescrito" in result.stderr


def test_install_script_is_idempotent_when_pipx_is_present(tmp_path: Path) -> None:
    fake_bin: Path = tmp_path / "bin"
    fake_bin.mkdir()
    _fake_python(fake_bin / "python3")
    pipx: Path = fake_bin / "pipx"
    pipx.write_text("#!/usr/bin/env sh\necho 'package tko 12.0.5'\n", encoding="utf-8")
    pipx.chmod(0o755)
    home: Path = tmp_path / "home"
    environment: dict[str, str] = {
        **os.environ,
        "HOME": str(home),
        "PATH": f"{fake_bin}:/usr/bin:/bin",
    }

    first = subprocess.run(
        ["/usr/bin/env", "bash", "install.sh"],
        cwd=Path(__file__).parents[1], env=environment, capture_output=True, text=True, check=False,
    )
    second = subprocess.run(
        ["/usr/bin/env", "bash", "install.sh"],
        cwd=Path(__file__).parents[1], env=environment, capture_output=True, text=True, check=False,
    )

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert "instalação do TKO via pipx" in first.stdout
    assert pipx.exists()