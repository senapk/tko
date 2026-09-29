import base64
from pathlib import Path

import pytest

from tko.feno.embed_local_assets import LocalAssetError, embed_local_assets, validate_local_assets


def test_embeds_markdown_reference_and_html_file_links(tmp_path: Path) -> None:
    activity: Path = tmp_path / "activity"
    activity.mkdir()
    (activity / "cover.png").write_bytes(b"png-content")
    (activity / "guide.pdf").write_bytes(b"pdf-content")
    (activity / "diagram.svg").write_text("<svg />", encoding="utf-8")
    (activity / "data.bin").write_bytes(b"binary")
    (activity / "docs").mkdir()

    content: str = (
        "![cover](cover.png)\n"
        "[Guide][guide]\n"
        "[guide]: <guide.pdf> \"PDF\"\n"
        "<img src='diagram.svg'>\n"
        '<a href="data.bin">Download</a>\n'
        "[folder](docs/) [anchor](#section) [external](https://example.com/file.png)\n"
        "`[example](missing.png)`\n"
        "```md\n![sample](missing-in-code.png)\n```\n"
    )

    result: str = embed_local_assets(content, activity)

    assert f"![cover](data:image/png;base64,{base64.b64encode(b'png-content').decode('ascii')})" in result
    assert (
        f"[guide]: <data:application/pdf;base64,{base64.b64encode(b'pdf-content').decode('ascii')}> \"PDF\""
        in result
    )
    assert f"src='data:image/svg+xml;base64,{base64.b64encode(b'<svg />').decode('ascii')}'" in result
    assert f'href="data:application/octet-stream;base64,{base64.b64encode(b"binary").decode("ascii")}"' in result
    assert "[folder](docs/)" in result
    assert "[anchor](#section)" in result
    assert "[external](https://example.com/file.png)" in result
    assert "`[example](missing.png)`" in result
    assert "![sample](missing-in-code.png)" in result


def test_missing_local_reference_raises_error(tmp_path: Path) -> None:
    with pytest.raises(LocalAssetError, match="does not exist: missing.png"):
        embed_local_assets("![missing](missing.png)", tmp_path)


def test_embedded_text_normalizes_windows_line_endings(tmp_path: Path) -> None:
    (tmp_path / "guide.md").write_bytes(b"# Guide\r\n")

    result: str = embed_local_assets("[Guide](guide.md)", tmp_path)

    normalized: str = base64.b64encode(b"# Guide\n").decode("ascii")
    assert result == f"[Guide](data:text/markdown;base64,{normalized})"


def test_reference_outside_activity_raises_error(tmp_path: Path) -> None:
    activity: Path = tmp_path / "activity"
    activity.mkdir()
    (tmp_path / "shared.png").write_bytes(b"outside")

    with pytest.raises(LocalAssetError, match="escapes the activity folder"):
        embed_local_assets("![outside](../shared.png)", activity)


def test_validation_checks_links_without_embedding(tmp_path: Path) -> None:
    (tmp_path / "image.png").write_bytes(b"content")

    validate_local_assets("![image](image.png)", tmp_path)
