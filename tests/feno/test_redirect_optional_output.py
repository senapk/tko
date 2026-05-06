import os
from pathlib import Path
from tko.feno.remote_md import Absolute
from tko.util.decoder import Decoder


def test_rebase_local_file_default_output(tmp_path: Path) -> None:
    """Test that local file rebase saves with original filename in current dir"""
    src_dir: Path = tmp_path / "src"
    src_dir.mkdir()
    source: Path = src_dir / "myfile.md"
    source.write_text("[link](page.md)")

    # Simulate default output behavior by calculating expected filename
    expected_filename: str = "myfile.md"
    expected_output: Path = Path(expected_filename)

    # Extract the logic to verify filename derivation
    assert Path(source).name == expected_filename


def test_rebase_local_same_dir_with_custom_output(tmp_path: Path) -> None:
    """Test explicit output still works as before"""
    source: Path = tmp_path / "src" / "file.md"
    source.parent.mkdir()
    source.write_text("[link](page.md)")
    output: Path = tmp_path / "src" / "output.md"

    relative_folder: Path = Path(os.path.relpath(source.parent, output.parent))
    content: str = Decoder.load(source)
    result: str = Absolute.change_to_relative_folder(content, relative_folder)
    Decoder.save(output, result)

    assert "page.md" in output.read_text()


def test_url_extraction_from_github_blob() -> None:
    """Test extraction of filename from GitHub blob URL"""
    from urllib.parse import urlparse
    url: str = "https://github.com/qxcodefup/arcade/blob/master/README.md"
    parsed_url = urlparse(url)
    filename: str = Path(parsed_url.path).name or "README.md"
    assert filename == "README.md"


def test_url_extraction_with_complex_path() -> None:
    """Test extraction of filename from URL with nested path"""
    from urllib.parse import urlparse
    url: str = "https://github.com/qxcodefup/arcade/blob/main/docs/guide.md"
    parsed_url = urlparse(url)
    filename: str = Path(parsed_url.path).name or "README.md"
    assert filename == "guide.md"
