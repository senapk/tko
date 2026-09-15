from rich.style import Style
from tko.ui_textual.palette import DARK, ERROR, INFO, LIGHT, ON_COLOR, WARNING, contrast_ratio
from tko.ui_textual.rt_adapter import to_rich_style, to_rich_text
from tko.util.rt import RT
from tko.util.text_style import TextStyle


def test_to_rich_text_preserves_content_and_runs() -> None:
    value = to_rich_text(RT.parse("[r]erro[] e [g*]sucesso[]"))

    assert value.plain == "erro e sucesso"
    assert len(value.spans) == 3
    style = value.spans[0].style
    assert isinstance(style, Style)
    assert style.color is not None and style.color.name == ERROR
    success_style = value.spans[2].style
    assert isinstance(success_style, Style)
    assert success_style.bold is True


def test_to_rich_text_keeps_unicode_content() -> None:
    value = to_rich_text(RT("ação ✓", "c_"))

    assert value.plain == "ação ✓"
    style = value.spans[0].style
    assert isinstance(style, Style)
    assert style.color is not None and style.color.name == INFO
    assert style.underline is True


def test_to_rich_style_maps_background_and_attributes() -> None:
    style = to_rich_style(TextStyle.parse("rY/!X"))

    assert style.color is not None
    assert style.bgcolor is not None and style.bgcolor.name == WARNING
    assert contrast_ratio(style.color.name, style.bgcolor.name) >= 4.5
    assert style.italic is True
    assert style.strike is True
    assert style.reverse is True


def test_background_only_style_has_explicit_readable_foreground() -> None:
    style = to_rich_style(TextStyle.parse("Y"))
    assert style.color is not None and style.color.name == ON_COLOR
    assert style.bgcolor is not None and style.bgcolor.name == WARNING


def test_plain_text_uses_active_palette_foreground() -> None:
    for palette in (DARK, LIGHT):
        value = to_rich_text(RT("texto comum"), palette)

        style = value.spans[0].style
        assert isinstance(style, Style)
        assert style.color is not None and style.color.name == palette.foreground


def test_all_palette_styles_have_explicit_readable_colors() -> None:
    for palette in (DARK, LIGHT):
        for foreground_code in ("", *palette.foregrounds):
            for background_code in ("", *palette.backgrounds):
                style = to_rich_style(TextStyle.parse(foreground_code + background_code), palette)

                assert style.color is not None
                if style.bgcolor is not None:
                    assert contrast_ratio(style.color.name, style.bgcolor.name) >= 4.5


def test_palette_pairs_have_readable_contrast() -> None:
    from tko.ui_textual.palette import contrast_ratio, readable_foreground

    for palette in (DARK, LIGHT):
        assert contrast_ratio(palette.muted, palette.background) >= 4.5
        for foreground in palette.foregrounds.values():
            for background in palette.foregrounds.values():
                assert contrast_ratio(readable_foreground(foreground, background, palette), background) >= 4.5
