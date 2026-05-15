from pathlib import Path
import builtins
from _pytest.monkeypatch import MonkeyPatch

import tko.feno.link_rebase as link_rebase_mod
from tko.feno.github_url_structure import GithubUrlStructure
from tko.feno.link_rebase import LinkRebase


def test_rebase_rewrites_image_file_and_folder_links() -> None:
    structure = GithubUrlStructure()
    structure.user = "user"
    structure.repo = "repo"
    structure.branch = "main"
    structure.relative_path = "docs"

    content = "![img](pic.png)\n[folder](sub/)\n[file](readme.md)"

    result = LinkRebase.rebase(content, structure)

    assert "![img](https://raw.githubusercontent.com/user/repo/main/docs/pic.png)" in result
    assert "[folder](https://github.com/user/repo/tree/main/docs/sub)" in result
    assert "[file](https://github.com/user/repo/blob/main/docs/readme.md)" in result


def test_rebase_task_markdown_link_from_github_downloaded_file() -> None:
    structure = GithubUrlStructure()
    structure.user = "qxcodefup"
    structure.repo = "arcade"
    structure.branch = "main"
    structure.relative_path = ""

    content = "- [ ]`@tres            :1:main`[Soma de três inteiros](base/tres/README.md)"

    result = LinkRebase.rebase(content, structure)

    assert "[Soma de três inteiros](https://github.com/qxcodefup/arcade/blob/main/base/tres/README.md)" in result


def test_convert_or_copy_or_print_writes_file_when_target_is_provided(tmp_path: Path) -> None:
    source = tmp_path / "input.md"
    source.write_text("[x](a.md)", encoding="utf-8")
    target = tmp_path / "out.md"

    LinkRebase.convert_or_copy_or_print(source, target, make_remote=False)

    assert target.read_text(encoding="utf-8") == "[x](a.md)\n"


def test_convert_or_copy_or_print_prints_when_target_is_none(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "input.md"
    source.write_text("[x](a.md)", encoding="utf-8")

    captured: dict[str, str] = {}

    class DummyCfg:
        def __init__(self, _target: Path, _make_remote: bool):
            pass

        def cfg_exists(self) -> bool:
            return True

        def calc_link_for_local_file(self) -> GithubUrlStructure:
            structure = GithubUrlStructure()
            structure.user = "user"
            structure.repo = "repo"
            structure.branch = "main"
            structure.relative_path = "docs"
            return structure

    monkeypatch.setattr(link_rebase_mod, "GithubCfg", DummyCfg)
    monkeypatch.setattr(link_rebase_mod.LinkRebase, "rebase", staticmethod(lambda _c, _r: "rebased")) # type: ignore
    monkeypatch.setattr(builtins, "print", lambda text: captured.setdefault("out", text)) # type: ignore

    LinkRebase.convert_or_copy_or_print(source, None, make_remote=True)

    assert captured["out"] == "rebased"
