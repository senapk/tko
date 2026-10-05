"""VPL input is raw text and must end before the output statement."""

from tko.loader.vpl_parser import VplParser
from tko.run.unit import Unit
from tko.run.writer import Writer


def test_vpl_writer_separates_empty_input_from_output() -> None:
    rendered: str = Writer.to_vpl(Unit(case="empty", input_data="", expected="ok\n"))

    assert rendered.startswith('case=empty\ninput=\noutput="ok\n"\n')
    assert VplParser.parse_vpl(rendered)[0].output == "ok\n"


def test_vpl_writer_keeps_input_as_raw_multiline_text() -> None:
    rendered: str = Writer.to_vpl(Unit(case="two lines", input_data="first\nsecond", expected="done\n"))

    assert 'input=first\nsecond\noutput="done\n"' in rendered
    assert VplParser.parse_vpl(rendered)[0].input == "first\nsecond\n"
