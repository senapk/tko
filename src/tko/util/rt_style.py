from __future__ import annotations
from dataclasses import dataclass, field
from functools import cache
from typing import Iterable

ANSI_RESET = "\033[0m"

FG_CODES = {
    "d": "",
    "k": "30",
    "r": "31",
    "g": "32",
    "y": "33",
    "b": "34",
    "m": "35",
    "c": "36",
    "w": "37",
}

BG_CODES = {
    "D": "",
    "K": "40",
    "R": "41",
    "G": "42",
    "Y": "43",
    "B": "44",
    "M": "45",
    "C": "46",
    "W": "47",
}

ATTR_CODES = {
    "*": "1",
    "_": "4",
    "/": "3",
    "X": "7",
    "!": "9",
}

FG_KEYS = frozenset(FG_CODES)
BG_KEYS = frozenset(BG_CODES)
ATTRS_KEYS = frozenset(ATTR_CODES)

CODES = {
    **FG_CODES,
    **BG_CODES,
    **ATTR_CODES,
}

ANSI_TO_FG = {
    v: k
    for k, v in FG_CODES.items()
}

ANSI_TO_BG = {
    v: k
    for k, v in BG_CODES.items()
}

ANSI_TO_ATTR = {
    v: k
    for k, v in ATTR_CODES.items()
}

def _empty_attrs() -> frozenset[str]:
    return frozenset()

@dataclass(frozen=True, slots=True)
class RTStyle:
    fg: str | None = None
    bg: str | None = None
    attrs: frozenset[str] = field(default_factory=_empty_attrs)

    @staticmethod
    @cache
    def parse(style: str) -> RTStyle:
        fg: str = "d"
        bg: str = "D"
        attrs: set[str] = set()

        for ch in style:
            if ch in FG_KEYS:
                fg = ch

            elif ch in BG_KEYS:
                bg = ch

            elif ch in ATTRS_KEYS:
                attrs.add(ch)

        return RTStyle(
            fg=fg,
            bg=bg,
            attrs=frozenset(attrs),
        )

    def overlay(self, other: RTStyle | str) -> RTStyle:
        if isinstance(other, str):
            other = RTStyle.parse(other)

        return RTStyle(
            fg=other.fg or self.fg,
            bg=other.bg or self.bg,
            attrs=self.attrs | other.attrs,
        )

    def clear_attrs(self) -> RTStyle:
        return RTStyle(
            fg=self.fg,
            bg=self.bg,
            attrs=frozenset(),
        )

    def is_plain(self) -> bool:
        # A style is considered plain if it has no foreground color, no background color, and no attributes.
        return (
            self.fg is None
            and self.bg is None
            and not self.attrs
        )
    
    @staticmethod
    def from_ansi_codes(
        codes: Iterable[str],
        base: RTStyle | None = None,
    ) -> RTStyle:
        fg = base.fg if base else None
        bg = base.bg if base else None
        attrs: set[str] = set(base.attrs) if base else set()

        for code in codes:
            # full reset
            if code == "0":
                fg = None
                bg = None
                attrs.clear()

            # foreground
            elif code in ANSI_TO_FG:
                fg = ANSI_TO_FG[code]

            # background
            elif code in ANSI_TO_BG:
                bg = ANSI_TO_BG[code]

            # attrs
            elif code in ANSI_TO_ATTR:
                attrs.add(ANSI_TO_ATTR[code])

        return RTStyle(
            fg=fg,
            bg=bg,
            attrs=frozenset(attrs),
        )

    def to_tag(self) -> str:
        """
        Convert the style to a tag string. The tag string is a concatenation of the foreground color, background color, 
        and attributes. The order of the attributes is sorted alphabetically.
        """
        parts: list[str] = []

        if self.fg:
            parts.append(self.fg)

        if self.bg:
            parts.append(self.bg)

        parts.extend(sorted(self.attrs))

        return "".join(parts)

    @cache
    def ansi(self) -> str:
        codes: list[str] = []

        if self.fg:
            codes.append(CODES[self.fg])

        if self.bg:
            codes.append(CODES[self.bg])

        for attr in sorted(self.attrs):
            codes.append(CODES[attr])

        return f"\033[{';'.join(codes)}m" if codes else ""    

    def __str__(self) -> str:
        return self.to_tag()
    
