from pathlib import Path
import shutil

import pytest

from tko.config.settings import Settings
from tko.run.solver_builder import SolverBuilder
from tko.util.runner import Runner


pytestmark = pytest.mark.skipif(
    shutil.which("kotlinc") is None or shutil.which("java") is None,
    reason="Kotlin integration requires kotlinc and java",
)


def test_solver_builder_compiles_and_runs_kotlin(tmp_path: Path) -> None:
    solver_path = tmp_path / "Main.kt"
    solver_path.write_text('fun main() {\n    println("Hello, World!")\n}\n', encoding="utf-8")

    solver = SolverBuilder([solver_path], Settings(tmp_path))
    executable, ok = solver.get_executable()

    assert ok is True
    assert executable.has_compile_error() is False

    cmd, folder = executable.get_command()
    assert isinstance(cmd, list)
    return_code, stdout, stderr = Runner.subprocess_run(cmd, folder=folder)

    assert return_code == 0, stdout + stderr
    assert stdout.strip() == "Hello, World!"
