import os
from pathlib import Path
from tko.feno.link_rebase import LinkRebase
from tko.util.decoder import Decoder


def test_redirect_local_same_dir(tmp_path: Path) -> None:
    source: Path = tmp_path / "src" / "file.md"
    source.parent.mkdir()
    source.write_text("[link](page.md)")
    output: Path = tmp_path / "src" / "output.md"

    relative_folder: Path = Path(os.path.relpath(source.parent, output.parent))
    content: str = Decoder.load(source)
    result: str = LinkRebase.change_to_relative_folder(content, relative_folder)
    Decoder.save(output, result)

    assert "page.md" in output.read_text()


def test_redirect_local_to_sibling_dir(tmp_path: Path) -> None:
    src_dir: Path = tmp_path / "src"
    src_dir.mkdir()
    source: Path = src_dir / "file.md"
    source.write_text("[link](page.md)")

    out_dir: Path = tmp_path / "out"
    out_dir.mkdir()
    output: Path = out_dir / "output.md"

    relative_folder: Path = Path(os.path.relpath(source.parent, output.parent))
    content: str = Decoder.load(source)
    result: str = LinkRebase.change_to_relative_folder(content, relative_folder)
    Decoder.save(output, result)

    assert "../src/page.md" in output.read_text()


def test_redirect_local_image_link(tmp_path: Path) -> None:
    src_dir: Path = tmp_path / "src"
    src_dir.mkdir()
    source: Path = src_dir / "file.md"
    source.write_text("![alt](image.png)")

    out_dir: Path = tmp_path / "out"
    out_dir.mkdir()
    output: Path = out_dir / "output.md"

    relative_folder: Path = Path(os.path.relpath(source.parent, output.parent))
    content: str = Decoder.load(source)
    result: str = LinkRebase.change_to_relative_folder(content, relative_folder)
    Decoder.save(output, result)

    assert "../src/image.png" in output.read_text()


def test_redirect_local_nested_source(tmp_path: Path) -> None:
    src_dir: Path = tmp_path / "a" / "b" / "c"
    src_dir.mkdir(parents=True)
    source: Path = src_dir / "file.md"
    source.write_text("[doc](readme.md)\n![img](logo.png)")

    out_dir: Path = tmp_path / "out"
    out_dir.mkdir()
    output: Path = out_dir / "output.md"

    relative_folder: Path = Path(os.path.relpath(source.parent, output.parent))
    content: str = Decoder.load(source)
    result: str = LinkRebase.change_to_relative_folder(content, relative_folder)
    Decoder.save(output, result)

    text: str = output.read_text()
    assert "../a/b/c/readme.md" in text
    assert "../a/b/c/logo.png" in text


def test_redirect_local_absolute_links_unchanged(tmp_path: Path) -> None:
    src_dir: Path = tmp_path / "src"
    src_dir.mkdir()
    source: Path = src_dir / "file.md"
    source.write_text("[external](https://github.com/user/repo)")

    out_dir: Path = tmp_path / "out"
    out_dir.mkdir()
    output: Path = out_dir / "output.md"

    relative_folder: Path = Path(os.path.relpath(source.parent, output.parent))
    content: str = Decoder.load(source)
    result: str = LinkRebase.change_to_relative_folder(content, relative_folder)
    Decoder.save(output, result)

    assert "https://github.com/user/repo" in output.read_text()


def test_redirect_local_empty_content(tmp_path: Path) -> None:
    src_dir: Path = tmp_path / "src"
    src_dir.mkdir()
    source: Path = src_dir / "file.md"
    source.write_text("")

    out_dir: Path = tmp_path / "out"
    out_dir.mkdir()
    output: Path = out_dir / "output.md"

    relative_folder: Path = Path(os.path.relpath(source.parent, output.parent))
    content: str = Decoder.load(source)
    result: str = LinkRebase.change_to_relative_folder(content, relative_folder)
    Decoder.save(output, result)

    assert output.read_text() == ""
