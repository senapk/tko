from pathlib import Path

import pytest

from tko.config.settings import Settings
from tko.run.solver_builder import SolverBuilder
from tko.util.runner import Runner


def test_solver_builder_uses_configured_typescript_commands(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "main.ts"
    source.write_text("export {};\nconsole.log('ok');\n", encoding="utf-8")
    languages_path = tmp_path / Settings.LANG_FILE
    languages_path.write_text(
        "[ts]\nbuild_cmd = ['custom-build', '{files}']\nrun_cmd = ['custom-run', '{entry}']\n",
        encoding="utf-8",
    )
    calls: list[tuple[list[str] | str, Path | None]] = []

    def fake_subprocess_run(
        cmd: str | list[str],
        input_data: str = "",
        timeout: float | None = None,
        folder: Path | None = None,
    ) -> tuple[int, str, str]:
        del input_data, timeout
        calls.append((cmd, folder))
        return 0, "", ""

    monkeypatch.setattr(Runner, "subprocess_run", fake_subprocess_run)

    executable, ok = SolverBuilder([source], Settings(tmp_path)).get_executable()

    assert ok is True
    assert calls == [(["custom-build", "main.ts"], tmp_path)]
    command, folder = executable.get_command()
    assert command == ["custom-run", (tmp_path / ".build" / "main.js").resolve().as_posix()]
    assert folder == tmp_path.resolve()
