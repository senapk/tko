from tko.ui_textual.rt_adapter import to_rich_style, to_rich_text
from tko.util.rt import RT
from tko.util.text_style import TextStyle


def test_to_rich_text_preserves_content_and_runs() -> None:
    value = to_rich_text(RT.parse("[r]erro[] e [g*]sucesso[]"))

    assert value.plain == "erro e sucesso"
    assert len(value.spans) == 2
    assert value.spans[0].style.color.name == "red"
    assert value.spans[1].style.bold is True


def test_to_rich_text_keeps_unicode_content() -> None:
    value = to_rich_text(RT("ação ✓", "c_"))

    assert value.plain == "ação ✓"
    assert value.spans[0].style.color.name == "cyan"
    assert value.spans[0].style.underline is True


def test_to_rich_style_maps_background_and_attributes() -> None:
    style = to_rich_style(TextStyle.parse("rY/!X"))

    assert style.color.name == "red"
    assert style.bgcolor.name == "yellow"
    assert style.italic is True
    assert style.strike is True
    assert style.reverse is True
