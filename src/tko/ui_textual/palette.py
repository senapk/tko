"""Single color registry for Textual widgets and TKO rich-text rendering.

Use semantic theme variables in CSS. Compact RT color codes are resolved here
so their appearance agrees with widgets instead of depending on terminal colors.
"""
from dataclasses import dataclass
from typing import Final

from textual.theme import Theme

@dataclass(frozen=True, slots=True)
class Palette:
    name: str
    background: str
    surface: str
    panel: str
    foreground: str
    muted: str
    border: str
    accent: str
    success: str
    warning: str
    error: str
    info: str
    special: str
    on_color: str

    @property
    def foregrounds(self) -> dict[str, str]:
        return {"k": self.background, "r": self.error, "g": self.success, "y": self.warning,
                "b": self.accent, "m": self.special, "c": self.info, "w": self.foreground}

    @property
    def backgrounds(self) -> dict[str, str]:
        return {key.upper(): value for key, value in self.foregrounds.items()}


DARK: Final[Palette] = Palette("tko-dark", "#101419", "#1b232d", "#232e3b", "#e6edf3", "#a5b3c2", "#59697c", "#82b6ff", "#8bd5a0", "#f0ce82", "#f2919a", "#8bd5dc", "#c6a0f6", "#101419")
LIGHT: Final[Palette] = Palette("tko-light", "#f7f9fb", "#e8edf3", "#d8e0e8", "#17212b", "#526273", "#8797a8", "#1769aa", "#18794e", "#8a5a00", "#b42318", "#087f8c", "#6941c6", "#f7f9fb")
THEMES: Final[dict[str, Palette]] = {DARK.name: DARK, LIGHT.name: LIGHT}

# Backward-compatible dark aliases for callers that imported these constants.
BACKGROUND, SURFACE, PANEL, TEXT, MUTED, BORDER = (DARK.background, DARK.surface, DARK.panel, DARK.foreground, DARK.muted, DARK.border)
ACCENT, SUCCESS, WARNING, ERROR, INFO, SPECIAL, ON_COLOR = (DARK.accent, DARK.success, DARK.warning, DARK.error, DARK.info, DARK.special, DARK.on_color)

FOREGROUND: Final[dict[str, str]] = DARK.foregrounds
BACKGROUND_COLORS: Final[dict[str, str]] = DARK.backgrounds


def make_theme(palette: Palette = DARK) -> Theme:
    return Theme(
        name=palette.name, primary=palette.accent, secondary=palette.info, accent=palette.accent,
        foreground=palette.foreground, background=palette.background, surface=palette.surface, panel=palette.panel,
        success=palette.success, warning=palette.warning, error=palette.error,
        dark=palette is DARK, text_alpha=1,
        variables={
            "text-muted": palette.muted, "border": palette.border,
            "input-background": palette.surface, "input-selection-background": palette.panel,
            "input-cursor-foreground": palette.on_color, "input-cursor-background": palette.accent,
            "block-cursor-foreground": palette.on_color, "block-cursor-background": palette.accent,
            "block-cursor-text-style": "bold",
            "footer-background": palette.background, "footer-key-foreground": palette.accent,
            "footer-description-foreground": palette.foreground, "button-color-foreground": palette.on_color,
            "tko-on-color": palette.on_color,
        },
    )


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(color: str) -> float:
        channels: list[float] = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear: list[float] = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
        return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

    first: float = luminance(foreground)
    second: float = luminance(background)
    return (max(first, second) + 0.05) / (min(first, second) + 0.05)


def readable_foreground(foreground: str, background: str, palette: Palette = DARK) -> str:
    if contrast_ratio(foreground, background) >= 4.5:
        return foreground
    return max(
        (palette.foreground, palette.on_color, "#000000", "#ffffff"),
        key=lambda color: contrast_ratio(color, background),
    )
