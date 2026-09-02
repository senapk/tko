from pathlib import Path

from tko.config.languages_settings import LanguagesSettings


def test_default_languages_include_kotlin() -> None:
    kotlin = LanguagesSettings.default_lang_settings["kt"]

    assert kotlin.build_cmd == ["kotlinc", "{files}", "-include-runtime", "-d", "{cache}/main.jar"]
    assert kotlin.run_cmd == ["java", "-jar", "{cache}/main.jar"]
    assert kotlin.draft == 'fun main() {\n    println("Hello, World!")\n}\n'


def test_languages_with_drafts_include_kotlin(tmp_path: Path) -> None:
    drafts = LanguagesSettings(tmp_path / "programming-languages.toml").get_languages_with_drafts()

    assert drafts["kt"] == LanguagesSettings.default_lang_settings["kt"].draft


def test_file_sample_includes_kotlin(tmp_path: Path) -> None:
    sample = LanguagesSettings(tmp_path / "programming-languages.toml").build_file_sample()

    assert "[kt]" in sample
    assert "build_cmd = ['kotlinc', '{files}', '-include-runtime', '-d', '{cache}/main.jar']" in sample
    assert "run_cmd = ['java', '-jar', '{cache}/main.jar']" in sample
