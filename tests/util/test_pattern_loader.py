from pathlib import Path

from tko.loader.loader import Loader
from tko.run.unit import Unit
from tko.run.writer import Writer
from tko.util.pattern_loader import DEFAULT_DIRECTORY_PATTERN, PatternLoader


def test_pattern_loader_matches_custom_directory_names():
    loader = PatternLoader("input-@.txt output-@.txt")

    sources = loader.get_file_sources(["input-01.txt", "output-01.txt"])

    assert len(sources) == 1
    assert sources[0].label == "01"
    assert sources[0].input_file == "input-01.txt"
    assert sources[0].output_file == "output-01.txt"


def test_loader_uses_standard_pattern_for_directories(tmp_path: Path):
    (tmp_path / "00.in").write_text("1\n", encoding="utf-8")
    (tmp_path / "00.sol").write_text("2\n", encoding="utf-8")

    units = Loader.parse_source(tmp_path)

    assert len(units) == 1
    assert units[0].get_input() == "1\n"
    assert units[0].get_expected() == "2\n"


def test_loader_accepts_explicit_read_pattern_for_directory(tmp_path: Path):
    (tmp_path / "input-01.txt").write_text("1\n", encoding="utf-8")
    (tmp_path / "output-01.txt").write_text("2\n", encoding="utf-8")

    units = Loader.parse_source(tmp_path, "input-@.txt output-@.txt")

    assert len(units) == 1
    assert units[0].get_input() == "1\n"
    assert units[0].get_expected() == "2\n"


def test_writer_uses_independent_write_pattern(tmp_path: Path):
    unit = Unit(case="", input_data="1\n", expected="2\n", source=Path("source"))

    Writer.save_target(
        tmp_path,
        [unit],
        quiet=True,
        pattern="input-@.txt output-@.txt",
    )

    assert (tmp_path / "input-00.txt").read_text(encoding="utf-8") == "1\n"
    assert (tmp_path / "output-00.txt").read_text(encoding="utf-8") == "2\n"


def test_writer_renders_toml_for_stdout():
    unit = Unit(case="sample", input_data="1\n", expected="2\n", source=Path("source"))

    rendered = Writer.render_toml([unit])

    assert rendered.startswith("[[tests]]\n")
    assert "label = 'sample'" in rendered
    assert "input = '''\n1\n'''" in rendered
    assert "output = '''\n2\n'''" in rendered


def test_default_directory_pattern_is_canonical():
    assert DEFAULT_DIRECTORY_PATTERN == "@.in @.sol"
