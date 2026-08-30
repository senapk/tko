from pathlib import Path

import pytest
import tko.feno.build as build_module


def test_build_all_moodle_writes_rebased_readme_and_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "repo"
    task = root / "base" / "soma"
    src = task / "src" / "py"
    src.mkdir(parents=True)
    (root / "remote.toml").write_text(
        'user = "user"\nrepository = "repo"\nbranch = "main"\n',
        encoding="utf-8",
    )
    (task / "README.md").write_text(
        "# Soma\n\n"
        "![cover](cover.png)\n"
        "[guia](docs/guide.md)\n"
        "[pasta](docs/)\n",
        encoding="utf-8",
    )
    (src / "solver.py").write_text(
        'print("visible") # @KEEP\n'
        "# @DROP\n"
        'print("hidden")\n',
        encoding="utf-8",
    )

    def fake_cases_run(cases_file: Path, source_readme: Path, source_dir: Path) -> None:
        cases_file.write_text("case=sample\ninput=\noutput=\"\"\n", encoding="utf-8")

    monkeypatch.setattr(build_module.Cases, "run", staticmethod(fake_cases_run))

    build_module.build_all(
        targets=[task],
        remote=True,
        check=False,
        erase=False,
        brief=True,
        moodle=True,
    )

    readme = (task / ".cache" / "README.md").read_text(encoding="utf-8")
    assert (
        "![cover](https://raw.githubusercontent.com/user/repo/main/base/soma/cover.png)"
        in readme
    )
    assert (
        "[guia](https://github.com/user/repo/blob/main/base/soma/docs/guide.md)"
        in readme
    )
    assert "[pasta](https://github.com/user/repo/tree/main/base/soma/docs/)" in readme
    assert (task / ".cache" / "README.html").is_file()
    assert (task / ".cache" / "tests.vpl").is_file()
    assert (task / ".cache" / "starter" / "py" / "solver.py").read_text(
        encoding="utf-8"
    ) == 'print("visible")\n'
    assert not (task / ".cache" / "mapi.json").exists()
