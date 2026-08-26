from tko.util.git_hub_url import GitHubUrl
from tko.feno.link_rebase import LinkRebase


def test_rebase_rewrites_image_file_and_folder_links() -> None:
    structure = GitHubUrl(
        user="user",
        repo="repo",
        branch="main",
        relative_path="docs",
    )

    content = r"""![img](pic.png)
[folder](sub/)
[file](readme.md)"""

    result = LinkRebase.rebase(content, structure).splitlines()

    assert "![img](https://raw.githubusercontent.com/user/repo/main/docs/pic.png)" == result[0]
    assert "[folder](https://github.com/user/repo/tree/main/docs/sub/)" == result[1]
    assert "[file](https://github.com/user/repo/blob/main/docs/readme.md)" == result[2]


def test_rebase_task_markdown_link_from_github_downloaded_file() -> None:
    structure = GitHubUrl(user="qxcodefup", repo="arcade", branch="main", relative_path="")

    content = "- [ ]`@tres            :1:main`[Soma de três inteiros](base/tres/README.md)"

    result = LinkRebase.rebase(content, structure)

    assert "- [ ]`@tres            :1:main`[Soma de três inteiros](https://github.com/qxcodefup/arcade/blob/main/base/tres/README.md)" in result


def test_rebase_uses_parent_folder_for_root_readme_url() -> None:
    structure = GitHubUrl(
        user="qxcodepoo",
        repo="arcade",
        branch="main",
        relative_path="README.md",
    )

    content = "- [ ] `@+main` [Criando a Main](wiki/main/README.md)"

    result = LinkRebase.rebase(content, structure)

    assert "[Criando a Main](https://github.com/qxcodepoo/arcade/blob/main/wiki/main/README.md)" in result


def test_rebase_uses_parent_folder_for_nested_markdown_url() -> None:
    structure = GitHubUrl(
        user="user",
        repo="repo",
        branch="main",
        relative_path="docs/guide.md",
    )

    content = "[next](chapter/page.md)"

    result = LinkRebase.rebase(content, structure)

    assert result == "[next](https://github.com/user/repo/blob/main/docs/chapter/page.md)"
