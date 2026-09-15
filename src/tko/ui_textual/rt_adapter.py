"""Adapters between TKO's presentation-neutral rich text and Rich."""

from rich.style import Style
from rich.text import Text

from tko.util.rt import RT
from tko.util.text_style import TextStyle


from tko.ui_textual.palette import DARK, Palette, readable_foreground


def to_rich_style(style: TextStyle, palette: Palette = DARK) -> Style:
    """Translate the compact TKO style alphabet to a Rich style."""
    background: str | None = palette.backgrounds.get(style.bg or "")
    foreground: str = palette.foregrounds.get(style.fg or "", palette.foreground)
    if background is not None and style.fg is None:
        foreground = palette.foreground if style.bg == "K" else palette.on_color
    if background is not None:
        foreground = readable_foreground(foreground, background, palette)
    return Style(
        color=foreground,
        bgcolor=background,
        bold="*" in style.attrs,
        underline="_" in style.attrs,
        italic="/" in style.attrs,
        reverse="X" in style.attrs,
        strike="!" in style.attrs,
    )


def to_rich_text(value: RT, palette: Palette = DARK) -> Text:
    """Return a Rich ``Text`` preserving RT runs and their styles."""
    text = Text()
    for style, content in value.runs:
        text.append(content, style=to_rich_style(style, palette))
    return text
