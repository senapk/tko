from tko.cli.cli_tool import _build_readme_candidates_from_repo_url # type: ignore


def test_build_readme_candidates_from_https_git_url() -> None:
    repo_url: str = "https://github.com/qxcodefup/arcade.git"
    out: list[str] = _build_readme_candidates_from_repo_url(repo_url)
    assert out == [
        "https://github.com/qxcodefup/arcade/blob/main/README.md",
    ]


def test_build_readme_candidates_from_https_plain_url() -> None:
    repo_url: str = "https://github.com/qxcodepoo/arcade"
    out: list[str] = _build_readme_candidates_from_repo_url(repo_url)
    assert out == [
        "https://github.com/qxcodepoo/arcade/blob/main/README.md",
    ]


def test_build_readme_candidates_from_git_ssh_url() -> None:
    repo_url: str = "git@github.com:qxcodeed/arcade.git"
    out: list[str] = _build_readme_candidates_from_repo_url(repo_url)
    assert out == [
        "https://github.com/qxcodeed/arcade/blob/main/README.md",
    ]
