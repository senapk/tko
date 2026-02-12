from __future__ import annotations
from typing import Callable

class MiniwiFontSolid:
    instace: MiniwiFontSolid | None = None
    font: dict[str, str] | None = None

    def get_instance(self) -> MiniwiFontSolid:
        if MiniwiFontSolid.instace is None:
            MiniwiFontSolid.instace = self
        return MiniwiFontSolid.instace

    QUAD = {
        0b0000: " ",
        0b0001: "▘",
        0b0010: "▝",
        0b0011: "▀",
        0b0100: "▖",
        0b0101: "▌",
        0b0110: "▞",
        0b0111: "▛",
        0b1000: "▗",
        0b1001: "▚",
        0b1010: "▐",
        0b1011: "▜",
        0b1100: "▄",
        0b1101: "▙",
        0b1110: "▟",
        0b1111: "█",
    }

    def quadblock(self, tl: str, tr: str, bl: str, br: str) -> str:
        value = (
            (tl == "1") << 0 |
            (tr == "1") << 1 |
            (bl == "1") << 2 |
            (br == "1") << 3
        )
        return MiniwiFontSolid.QUAD[value]

    def build_glyph4(self, bitmap: list[str]) -> str:
        rows: list[str] = []

        for y in range(0, len(bitmap), 2):
            row = ""
            for x in range(0, len(bitmap[0]), 2):
                row += self.quadblock(
                    bitmap[y][x],
                    bitmap[y][x+1],
                    bitmap[y+1][x],
                    bitmap[y+1][x+1],
                )
            rows.append(row)

        return "\n".join(rows)

class MiniwiFontDotted:
    def braille_char(self, grid: list[list[str]]) -> str:
        # Braille Unicode bit mapping (2x4 grid)
        # 1 4
        # 2 5
        # 3 6
        # 7 8
        val = 0
        if grid[0][0] == "1": val |= 0x01
        if grid[1][0] == "1": val |= 0x02
        if grid[2][0] == "1": val |= 0x04
        if grid[0][1] == "1": val |= 0x08
        if grid[1][1] == "1": val |= 0x10
        if grid[2][1] == "1": val |= 0x20
        if grid[3][0] == "1": val |= 0x40
        if grid[3][1] == "1": val |= 0x80
        return chr(0x2800 + val)

    def build_glyph8(self, bitmap: list[str]) -> str:
        rows: list[str] = []
        height = len(bitmap)
        width = len(bitmap[0])

        for y in range(0, height, 4):
            row = ""
            for x in range(0, width, 2):
                # Create a 4x2 sub-grid, padding with '0' if out of bounds
                sub_grid: list[list[str]] = []
                for dy in range(4):
                    grid_row: list[str] = []
                    for dx in range(2):
                        if (y + dy) < height and (x + dx) < width:
                            grid_row.append(bitmap[y + dy][x + dx])
                        else:
                            grid_row.append("0")
                    sub_grid.append(grid_row)
                row += self.braille_char(sub_grid)
            rows.append(row)

        return "\n".join(rows)

class MiniwiBuilder:

    instance: MiniwiBuilder | None = None
    font8: dict[str, str] | None = None
    font4: dict[str, str] | None = None

    def get_instance(self) -> MiniwiBuilder:
        if MiniwiBuilder.instance is None:
            MiniwiBuilder.instance = self
        return MiniwiBuilder.instance

    def get_font4(self) -> dict[str, str]:
        if MiniwiBuilder.font4 is None:
            MiniwiBuilder.font4 = self.__get_font(MiniwiFontSolid().build_glyph4)
        return MiniwiBuilder.font4

    def get_font8(self) -> dict[str, str]:
        if MiniwiBuilder.font8 is None:
            MiniwiBuilder.font8 = self.__get_font(MiniwiFontDotted().build_glyph8)
        return MiniwiBuilder.font8

    @staticmethod
    def __get_font(builder: Callable[[list[str]], str]) -> dict[str, str]:
        return  {
            "a": builder([ "0000", "0000", "1110", "0010", "1110", "1110", "0000", "0000", ]),
            "b": builder([ "1000", "1000", "1110", "1010", "1010", "1110", "0000", "0000", ]),
            "c": builder([ "0000", "0000", "1110", "1000", "1000", "1110", "0000", "0000", ]),
            "d": builder([ "0010", "0010", "1110", "1010", "1010", "1110", "0000", "0000", ]),
            "e": builder([ "0000", "0000", "1110", "1110", "1000", "1110", "0000", "0000", ]),
            "f": builder([ "0110", "0100", "1110", "0100", "0100", "0100", "0000", "0000", ]),
            "g": builder([ "0000", "0000", "1110", "1010", "1110", "0010", "1110", "0000", ]),
            "h": builder([ "1000", "1000", "1110", "1010", "1010", "1010", "0000", "0000", ]),
            "i": builder([ "0100", "0000", "1100", "0100", "0100", "1110", "0000", "0000", ]),
            "j": builder([ "0010", "0000", "0110", "0010", "0010", "0010", "1010", "1110", ]),
            "k": builder([ "1000", "1000", "1010", "1100", "1100", "1010", "0000", "0000", ]),
            "l": builder([ "1100", "0100", "0100", "0100", "0100", "1110", "0000", "0000", ]),
            "m": builder([ "000000", "000000", "110110", "111110", "101010", "101010", "000000", "000000", ]),
            "n": builder([ "0000", "0000", "1110", "1010", "1010", "1010", "0000", "0000", ]),
            "o": builder([ "0000", "0000", "1110", "1010", "1010", "1110", "0000", "0000", ]),
            "p": builder([ "0000", "0000", "1110", "1010", "1010", "1110", "1000", "1000", ]),
            "q": builder([ "0000", "0000", "1110", "1010", "1010", "1110", "0010", "0010", ]),
            "r": builder([ "0000", "0000", "1110", "1000", "1000", "1000", "0000", "0000", ]),
            "s": builder([ "0000", "0000", "1110", "1000", "0010", "1110", "0000", "0000", ]),
            "t": builder([ "0000", "0100", "1110", "0100", "0100", "0110", "0000", "0000", ]),
            "T": builder([ "0000", "1110", "0100", "0100", "0100", "0100", "0000", "0000", ]),
            "u": builder([ "0000", "0000", "1010", "1010", "1010", "1110", "0000", "0000", ]),
            "v": builder([ "0000", "0000", "1010", "1010", "1010", "0100", "0000", "0000", ]),
            "x": builder([ "0000", "0000", "1010", "0100", "0100", "1010", "0000", "0000", ]),
            "y": builder([ "0000", "0000", "1010", "1010", "1010", "1110", "0010", "1110", ]),
            "z": builder([ "0000", "0000", "1110", "0010", "0100", "1110", "0000", "0000", ]),
            "A": builder([ "0000", "1110", "1010", "1110", "1010", "1010", "0000", "0000", ]),
            "B": builder([ "0000", "1100", "1010", "1100", "1010", "1100", "0000", "0000", ]),
            "C": builder([ "0000", "1110", "1000", "1000", "1000", "1110", "0000", "0000", ]),
            "D": builder([ "0000", "1100", "1010", "1010", "1010", "1100", "0000", "0000", ]),
            "E": builder([ "0000", "1110", "1000", "1110", "1000", "1110", "0000", "0000", ]),
            "F": builder([ "0000", "1110", "1000", "1110", "1000", "1000", "0000", "0000", ]),
            "G": builder([ "0000", "1110", "1000", "1000", "1010", "1110", "0000", "0000", ]),
            "H": builder([ "0000", "1010", "1010", "1110", "1010", "1010", "0000", "0000", ]),
            "I": builder([ "0000", "1110", "0100", "0100", "0100", "1110", "0000", "0000", ]),
            "J": builder([ "0000", "0010", "0010", "0010", "1010", "1110", "0000", "0000", ]),
            "K": builder([ "0000", "1010", "1100", "1100", "1010", "1010", "0000", "0000", ]),
            "L": builder([ "0000", "1000", "1000", "1000", "1000", "1110", "0000", "0000", ]),
            "M": builder([ "00000000", "11000110", "10101010", "10010010", "10000010", "10000010", "00000000", "00000000", ]),
            "N": builder([ "000000", "100010", "110010", "101010", "100110", "100010", "000000", "000000", ]),
            "O": builder([ "0000", "1110", "1010", "1010", "1010", "1110", "0000", "0000", ]),
            "P": builder([ "0000", "1110", "1010", "1110", "1000", "1000", "0000", "0000", ]),
            "Q": builder([ "0000", "1110", "1010", "1010", "1110", "1110", "0010", "0000", ]),
            "R": builder([ "0000", "1110", "1010", "1110", "1100", "1010", "0000", "0000", ]),
            "S": builder([ "0000", "1110", "1000", "0100", "0010", "1110", "0000", "0000", ]),
            "U": builder([ "0000", "1010", "1010", "1010", "1010", "1110", "0000", "0000", ]),
            "V": builder([ "0000", "1010", "1010", "1010", "1010", "0100", "0000", "0000", ]),
            "W": builder([ "00000000", "10000010", "10000010", "10010010", "10101010", "11000110", "00000000", "00000000", ]),
            "X": builder([ "0000", "1010", "1010", "0100", "1010", "1010", "0000", "0000", ]),
            "Y": builder([ "0000", "1010", "1010", "10100", "0100", "0100", "0000", "0000", ]),
            "Z": builder([ "0000", "1110", "0010", "0100", "1000", "1110", "0000", "0000", ]),
            " ": builder([ "00", "00", "00", "00", "00", "00", "00", "00", ]),
            "_": builder([ "0000", "0000", "0000", "0000", "0000", "1110", "0000", "0000", ]),
            "-": builder([ "0000", "0000", "0000", "0000", "1110", "0000", "0000", "0000", ]),
            "@": builder([ "000000", "011100", "100010", "101010", "101110", "100000", "011100", "000000", ]),
        }

class Miniwi:
    @staticmethod
    def render_solid(text: str) -> str:
        miniwi = MiniwiBuilder().get_instance()
        return Miniwi.__render(text, miniwi.get_font4())
    
    @staticmethod
    def render_dotted(text: str) -> str:
        miniwi = MiniwiBuilder().get_instance()
        return Miniwi.__render(text, miniwi.get_font8())

    @staticmethod
    def __render(text: str, font: dict[str, str]) -> str:
        lines: list[str] = []
        for char in text:
            if char not in font:
                continue
            glyph = font.get(char, "").splitlines()
            for i, line in enumerate(glyph):
                if len(lines) <= i:
                    lines.append("")
                lines[i] += line
        return "\n".join(lines)

if __name__ == "__main__":
    print(Miniwi.render_solid("@Julia gosta de suco de agulha"))
    print(Miniwi.render_dotted("@Julia gosta de suco de agulha"))
