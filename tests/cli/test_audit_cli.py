from pathlib import Path
from types import SimpleNamespace
from typing import Any
import json
import re

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

import tko.cli.audit_preview as audit_preview
from tko.cli.cli_audit import app
from tko.config.run_settings import RunSettings
from tko.config.settings import Settings
from tko.util.console import Console


def _extract_output_dir(output: str) -> Path:
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")
    lines = [ansi_re.sub("", line).strip() for line in output.splitlines()]

    for line in lines:
        if not line:
            continue
        candidate = Path(line)
        if candidate.is_dir() and candidate.name.startswith("tko-audit-unpack-"):
            return candidate

    for line in lines:
        if not line:
            continue
        candidate = Path(line)
        if candidate.is_dir():
            return candidate

    raise AssertionError(f"Could not find unpack output directory in output:\n{output}")


def _make_app_context(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path / "settings")
    settings.rs = RunSettings(changedir=tmp_path)
    return settings


def test_audit_starts_watcher_with_verbose_and_interval(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)

    repo = SimpleNamespace(audit=SimpleNamespace(enabled=False, interval_seconds=None))
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

    with Console.capture() as out:
        result = runner.invoke(app, ["init", "--interval", "15"], obj=ctx)
    combined_output = result.output + out.getvalue()

    assert result.exit_code == 0
    assert captured["repo"] is repo
    assert captured["log_edits"] is False
    assert captured["log_audit"] is True
    assert captured["audit_verbose"] is True
    assert captured["audit_interval_seconds"] == 15
    assert captured["stopped"] is True
    assert "Abra o tko em outro terminal para fazer as tarefas" in combined_output


def test_audit_unpack_jsonl_creates_temp_files(tmp_path: Path) -> None:
    runner = CliRunner()
    source_file = tmp_path / "draft.c.jsonl"
    source_file.write_text(
        '{"ts":1781111341,"label":"2026/06/10-14:09:01","hash":"d707acdef8b37b48726e04257e8f3f3a6d46463a45d5fcf19e888ab50cd677a0","content":"int main() {\\n    return 0;\\n}\\n"}\n'
        '{"ts":1781111380,"hash":"5068ec625665b22d73c171bbc831ef14235986a7af6d2759c14b7c82649154c6","content":"int main() {\\n    return 1;\\n}\\n"}\n',
        encoding="utf-8",
    )

    with Console.capture() as out:
        result = runner.invoke(app, ["unpack", str(source_file)])
    combined_output = result.output + out.getvalue()

    assert result.exit_code == 0
    output_dir = _extract_output_dir(combined_output)
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

    with Console.capture() as out:
        result = runner.invoke(app, ["unpack", str(source_file)])
    combined_output = result.output + out.getvalue()

    assert result.exit_code == 0
    output_dir = _extract_output_dir(combined_output)
    extracted_files = sorted(output_dir.iterdir())
    assert len(extracted_files) == 1
    assert extracted_files[0].read_text(encoding="utf-8") == "print(2)\n"


def test_audit_set_on_persists_flag(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)

    repo = SimpleNamespace(audit=SimpleNamespace(enabled=False, interval_seconds=None))
    captured: dict[str, Any] = {"saved": False}

    def fake_load_repo(*_args: Any, **_kwargs: Any) -> tuple[SimpleNamespace, Path]:
        return repo, tmp_path

    def fake_save(self: Any) -> Any:
        captured["saved"] = True
        return self

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)
    monkeypatch.setattr("tko.repository.repository_config.RepositoryConfig.save", fake_save)

    with Console.capture() as out:
        result = runner.invoke(app, ["set", "--on"], obj=ctx)
    combined_output = result.output + out.getvalue()

    assert result.exit_code == 0
    assert repo.audit.enabled is True
    assert captured["saved"] is True
    assert "Auditoria persistente habilitada" in combined_output


def test_audit_set_off_persists_flag(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    ctx = _make_app_context(tmp_path)

    repo = SimpleNamespace(audit=SimpleNamespace(enabled=True, interval_seconds=None))
    captured: dict[str, Any] = {"saved": False}

    def fake_load_repo(*_args: Any, **_kwargs: Any) -> tuple[SimpleNamespace, Path]:
        return repo, tmp_path

    def fake_save(self: Any) -> Any:
        captured["saved"] = True
        return self

    monkeypatch.setattr("tko.cli.common.load_repo", fake_load_repo)
    monkeypatch.setattr("tko.repository.repository_config.RepositoryConfig.save", fake_save)

    with Console.capture() as out:
        result = runner.invoke(app, ["set", "--off"], obj=ctx)
    combined_output = result.output + out.getvalue()

    assert result.exit_code == 0
    assert repo.audit.enabled is False
    assert captured["saved"] is True
    assert "Auditoria persistente desabilitada" in combined_output


def test_audit_preview_render_first_file_outputs_content(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    index_file = tmp_path / "index"
    snapshot = tmp_path / "2026-06-10_14-09-01_solver.py"
    snapshot.write_text("print('ok')\n", encoding="utf-8")
    index_file.write_text(str(snapshot), encoding="utf-8")

    monkeypatch.setattr(audit_preview, "which", lambda _name: None)

    result = runner.invoke(
        app,
        ["preview", "--index-file", str(index_file), "--preview-index", "1"],
    )

    assert result.exit_code == 0
    assert "\033[33mElapsed=" in result.output
    assert "Elapsed=" in result.output
    assert str(snapshot) in result.output
    assert "print('ok')" in result.output


def test_audit_preview_elapsed_ignores_unpack_index_prefix(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    index_file = tmp_path / "index"
    first = tmp_path / "0001_2026-06-10_14-09-01_solver.py"
    second = tmp_path / "0002_2026-06-10_14-10-01_solver.py"
    first.write_text("print(1)\n", encoding="utf-8")
    second.write_text("print(2)\n", encoding="utf-8")
    index_file.write_text(f"{first}\n{second}", encoding="utf-8")

    monkeypatch.setattr(audit_preview, "which", lambda _name: None)

    result = runner.invoke(
        app,
        ["preview", "--index-file", str(index_file), "--preview-index", "2"],
    )

    assert result.exit_code == 0
    assert "Elapsed=\033[32m00:01:00" in result.output


def test_audit_preview_invokes_fzf_with_numbered_files(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    source_dir = tmp_path / "snapshots"
    source_dir.mkdir()
    first = source_dir / "2026-06-10_14-09-01_solver.py"
    second = source_dir / "2026-06-10_14-10-01_solver.py"
    first.write_text("print(1)\n", encoding="utf-8")
    second.write_text("print(2)\n", encoding="utf-8")
    captured: dict[str, Any] = {}

    def fake_run(args: list[str], input: str | None = None, text: bool = False, **_kwargs: Any) -> SimpleNamespace:
        captured["args"] = args
        captured["input"] = input
        captured["text"] = text
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(audit_preview, "which", lambda name: "/usr/bin/fzf" if name == "fzf" else None)
    monkeypatch.setattr(audit_preview.subprocess, "run", fake_run)

    result = runner.invoke(app, ["preview", str(source_dir)])

    assert result.exit_code == 0
    assert captured["args"][0] == "fzf"
    assert "--preview" in captured["args"]
    preview_command = captured["args"][captured["args"].index("--preview") + 1]
    assert "-m tko.cli.audit_preview" in preview_command
    assert "--preview-index {1}" in preview_command
    assert captured["input"] == f"1\t{first}\n2\t{second}"
    assert captured["text"] is True
