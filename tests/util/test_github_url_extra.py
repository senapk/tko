from pathlib import Path
from _pytest.monkeypatch import MonkeyPatch

import tko.util.github_url as github_url_mod
from tko.feno.github_url_structure import GithubUrlStructure
from tko.util.github_url import GitHubUrl


def test_github_url_fixed_url_empty_when_state_is_incomplete() -> None:
    url = GitHubUrl("https://gist.githubusercontent.com/user/abc123/raw/abc/file.md")
    url.raw_link = ""
    url.url_structure = None

    assert url.fixed_url == ""


def test_github_url_download_and_rebase_calls_pipeline(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    url = GitHubUrl("https://github.com/user/repo/blob/main/folder/file.md")
    downloaded = tmp_path / "downloaded.md"
    downloaded.write_text("irrelevant", encoding="utf-8")
    output_file = tmp_path / "out.md"

    calls: dict[str, object] = {}

    def fake_urlretrieve(remote: str, filename: str):
        calls["url"] = remote
        calls["filename"] = filename
        return str(downloaded), None

    def fake_load(path: str) -> str:
        calls["load_path"] = path
        return "source content"

    def fake_rebase(content: str, structure: GithubUrlStructure) -> str:
        calls["rebase_content"] = content
        calls["rebase_branch"] = structure.branch
        return "rebased content"

    def fake_save(path: str, content: str) -> None:
        calls["save_path"] = path
        calls["save_content"] = content

    monkeypatch.setattr(github_url_mod.urllib.request, "urlretrieve", fake_urlretrieve)
    monkeypatch.setattr(github_url_mod.Decoder, "load", fake_load)
    monkeypatch.setattr(github_url_mod.LinkRebase, "rebase", staticmethod(fake_rebase))
    monkeypatch.setattr(github_url_mod.Decoder, "save", fake_save)

    url.download_and_rebase(str(output_file))

    assert calls["url"] == "https://raw.githubusercontent.com/user/repo/main/folder/file.md"
    assert calls["filename"] == str(output_file)
    assert calls["load_path"] == str(downloaded)
    assert calls["rebase_content"] == "source content"
    assert calls["rebase_branch"] == "main"
    assert calls["save_path"] == str(output_file)
    assert calls["save_content"] == "rebased content"


def test_github_url_structure_repository_and_github_urls() -> None:
    structure = GithubUrlStructure()
    structure.user = "user"
    structure.repo = "repo"
    structure.branch = "main"
    structure.relative_path = "folder/file.md"

    assert structure.repository_url == "https://github.com/user/repo"
    assert structure.github_url == "https://github.com/user/repo/blob/main/folder/file.md"


def test_github_url_structure_parses_raw_githubusercontent_url() -> None:
    structure = GithubUrlStructure()

    ok = structure.parse(
        "https://raw.githubusercontent.com/user/repo/refs/heads/main/folder/file.md"
    )

    assert ok is True
    assert structure.user == "user"
    assert structure.repo == "repo"
    assert structure.branch == "main"
    assert structure.relative_path == "folder/file.md"
