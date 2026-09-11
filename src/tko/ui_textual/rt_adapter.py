"""Adapters between TKO's presentation-neutral rich text and Rich."""

from rich.style import Style
from rich.text import Text

from tko.util.rt import RT
from tko.util.text_style import TextStyle


_FOREGROUND = {
    "k": "black",
    "r": "red",
    "g": "green",
    "y": "yellow",
    "b": "blue",
    "m": "magenta",
    "c": "cyan",
    "w": "white",
}

_BACKGROUND = {
    "K": "black",
    "R": "red",
    "G": "green",
    "Y": "yellow",
    "B": "blue",
    "M": "magenta",
    "C": "cyan",
    "W": "white",
}


def to_rich_style(style: TextStyle) -> Style:
    """Translate the compact TKO style alphabet to a Rich style."""
    return Style(
        color=_FOREGROUND.get(style.fg or ""),
        bgcolor=_BACKGROUND.get(style.bg or ""),
        bold="*" in style.attrs,
        underline="_" in style.attrs,
        italic="/" in style.attrs,
        reverse="X" in style.attrs,
        strike="!" in style.attrs,
    )


def to_rich_text(value: RT) -> Text:
    """Return a Rich ``Text`` preserving RT runs and their styles."""
    text = Text()
    for style, content in value.runs:
        # Rich records an explicit empty Style as a span. Keep plain RT runs
        # plain so the resulting model has the same meaningful runs as RT.
        if style.is_plain():
            text.append(content)
        else:
            text.append(content, style=to_rich_style(style))
    return text
