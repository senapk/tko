from pathlib import Path
from types import SimpleNamespace
from typing import Any
import json

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from tko.cli.cli_audit import app
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings


def _make_app_context(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path / "settings")
    settings.rs = RunSettings(changedir=tmp_path, local_cache=True)
    return settings


def test_audit_starts_watcher_with_verbose_and_interval(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)

    repo = SimpleNamespace()
    captured: dict[str, Any] = {"stopped": False}

    def fake_load_repo(*_args: Any, **_kwargs: Any) -> tuple[SimpleNamespace, Path]:
        return repo, tmp_path

    class DummyWatcher:
        def __init__(self, _repo: object):
            captured["repo"] = _repo

        def start_watching(
            self,
            log_edits: bool = True,
            log_audit: bool = False,
            audit_verbose: bool = False,
            audit_interval_seconds: int | None = None,
        ) -> "DummyWatcher":
            captured["log_edits"] = log_edits
            captured["log_audit"] = log_audit
            captured["audit_verbose"] = audit_verbose
            captured["audit_interval_seconds"] = audit_interval_seconds
            return self

        def stop_watching(self) -> "DummyWatcher":
            captured["stopped"] = True
            return self

    def fake_sleep(_seconds: float) -> None:
        raise KeyboardInterrupt()

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)
    monkeypatch.setattr("tko.repository.repository_watcher.RepositoryWatcher", DummyWatcher)
    monkeypatch.setattr("time.sleep", fake_sleep)

    result = runner.invoke(app, ["init", "--interval", "15"], obj=ctx)

    assert result.exit_code == 0
    assert captured["repo"] is repo
    assert captured["log_edits"] is False
    assert captured["log_audit"] is True
    assert captured["audit_verbose"] is True
    assert captured["audit_interval_seconds"] == 15
    assert captured["stopped"] is True
    assert "Audit watcher started" in result.output
    assert "Audit watcher stopped" in result.output


def test_audit_unpack_jsonl_creates_temp_files(tmp_path: Path) -> None:
    runner = CliRunner()
    source_file = tmp_path / "draft.c.jsonl"
    source_file.write_text(
        '{"ts":1781111341,"label":"2026/06/10-14:09:01","hash":"d707acdef8b37b48726e04257e8f3f3a6d46463a45d5fcf19e888ab50cd677a0","content":"int main() {\\n    return 0;\\n}\\n"}\n'
        '{"ts":1781111380,"hash":"5068ec625665b22d73c171bbc831ef14235986a7af6d2759c14b7c82649154c6","content":"int main() {\\n    return 1;\\n}\\n"}\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["unpack", str(source_file)])

    assert result.exit_code == 0
    output_dir = Path(result.output.strip().splitlines()[0])
    extracted_files = sorted(output_dir.iterdir())
    assert len(extracted_files) == 2
    assert extracted_files[0].read_text(encoding="utf-8") == "int main() {\n    return 0;\n}\n"
    assert extracted_files[1].read_text(encoding="utf-8") == "int main() {\n    return 1;\n}\n"


def test_audit_unpack_patch_history_json_creates_temp_files(tmp_path: Path) -> None:
    runner = CliRunner()
    source_file = tmp_path / "solver.py.json"
    source_file.write_text(
        json.dumps(
            {
                "patches": [
                    {"label": "2026-06-10_14-00-00", "content": "print(1)\n", "lines": "1"},
                    {"label": "2026-06-10_14-01-00", "content": "print(2)\n", "lines": "1"},
                ]
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["unpack", str(source_file)])

    assert result.exit_code == 0
    output_dir = Path(result.output.strip().splitlines()[0])
    extracted_files = sorted(output_dir.iterdir())
    assert len(extracted_files) == 1
    assert extracted_files[0].read_text(encoding="utf-8") == "print(2)\n"
