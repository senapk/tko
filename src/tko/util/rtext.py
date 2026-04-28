from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Any
from wcwidth import wcwidth
import enum
import re

Run = tuple[str, str]  # (style, text)

ATTR = {
    ".": "\033[0m",  # reset
    "*": "\033[1m",  # bold
    "_": "\033[4m",  # underline
    "/": "\033[3m",  # italic
    "X": "\033[7m",  # reverse
    "!": "\033[9m",  # strikethrough
}
FG = {
    "k": "\033[30m",  # black
    "r": "\033[31m",  # red
    "g": "\033[32m",  # green
    "y": "\033[33m",  # yellow
    "b": "\033[34m",  # blue
    "m": "\033[35m",  # magenta
    "c": "\033[36m",  # cyan
    "w": "\033[37m",  # white
}

BG = {
    "K": "\033[40m",  # black
    "R": "\033[41m",  # red
    "G": "\033[42m",  # green
    "Y": "\033[43m",  # yellow
    "B": "\033[44m",  # blue
    "M": "\033[45m",  # magenta
    "C": "\033[46m",  # cyan
    "W": "\033[47m",  # white
}

ANSI = {**ATTR, **FG, **BG}

def ansi(style: str) -> str:
    return "".join(ANSI.get(s, "") for s in style)

def normalize_style(style: str) -> str:
    fg: list[str] = []
    bg: list[str] = []
    attr: list[str] = []
    for c in style:
        if c in FG:
            fg = [c]
        elif c in BG:
            bg = [c]
        elif c in ATTR and c not in attr:
            attr.append(c)
    return "".join(attr + fg + bg)

class RenderMode(enum.Enum):
    ANSI = "ansi"
    PLAIN = "plain"
    DEBUG = "debug"

class RenderConfig:
    mode: RenderMode = RenderMode.ANSI
    enabled: bool = True


@dataclass(frozen=True)
class RText:
    runs: tuple[Run, ...] = ()

    def __init__(self, text: str = "", style: str = "", runs: Iterable[Run] | None = None):
        if runs is not None:
            object.__setattr__(self, "runs", tuple(self._merge(runs)))
        elif text:
            object.__setattr__(self, "runs", ((normalize_style(style), text),))
        else:
            object.__setattr__(self, "runs", ())

    @staticmethod
    def run(style: str, text: str) -> RText:
        return RText(text, style)

    @staticmethod
    def from_runs(runs: Iterable[Run]) -> RText:
        return RText(runs=runs)

    @staticmethod
    def decode_raw(data: str) -> RText:
        ansi_to_style = {
            "\033[30m": "k",
            "\033[31m": "r",
            "\033[32m": "g",
            "\033[33m": "y",
            "\033[34m": "b",
            "\033[35m": "m",
            "\033[36m": "c",
            "\033[37m": "w",
            "\033[40m": "K",
            "\033[41m": "R",
            "\033[42m": "G",
            "\033[43m": "Y",
            "\033[44m": "B",
            "\033[45m": "M",
            "\033[46m": "C",
            "\033[47m": "W",
            "\033[0m": "",
        }
        pattern = "|".join(re.escape(key) for key in ansi_to_style)
        if not pattern:
            return RText(data)

        runs: list[Run] = []
        style = ""
        last_idx = 0
        for match in re.finditer(pattern, data):
            if match.start() > last_idx:
                runs.append((style, data[last_idx:match.start()]))
            style = ansi_to_style[match.group(0)]
            last_idx = match.end()
        if last_idx < len(data):
            runs.append((style, data[last_idx:]))
        return RText.from_runs(runs)

    @staticmethod
    def format(template: str = "", *args: Any) -> RText:
        runs: list[Run] = []
        arg_i = 0
        i = 0

        def append(value: Any, style: str = "") -> None:
            if value is None:
                return
            if isinstance(value, RText):
                if style:
                    runs.extend((normalize_style(style), text) for _, text in value.runs)
                else:
                    runs.extend(value.runs)
            elif isinstance(value, tuple) and len(value) == 2: # type: ignore
                value_style, text = value # type: ignore
                runs.append((normalize_style(style or str(value_style)), str(text))) # type: ignore
            else:
                runs.append((normalize_style(style), str(value))) # type: ignore

        while i < len(template):
            if template[i:i + 2] == "{{":
                append("{")
                i += 2
                continue
            if template[i:i + 2] == "}}":
                append("}")
                i += 2
                continue
            if template[i] != "{":
                j = template.find("{", i)
                if j == -1:
                    j = len(template)
                append(template[i:j])
                i = j
                continue

            j = template.find("}", i)
            if j == -1:
                append(template[i])
                i += 1
                continue

            token = template[i + 1:j]
            style, inline = (token.split(":", 1) + [""])[:2] if ":" in token else (token, "")
            if inline:
                append(inline, style)
            elif arg_i < len(args):
                append(args[arg_i], style)
                arg_i += 1
            else:
                append("", style)
            i = j + 1

        for arg in args[arg_i:]:
            append(arg)
        return RText.from_runs(runs)

    @staticmethod
    def concat(*texts: RText) -> RText:
        runs: list[Run] = []
        for t in texts:
            runs.extend(t.runs)
        return RText(runs=runs)

    @staticmethod
    def join(texts: Iterable[RText], sep: RText) -> RText:
        texts = list(texts)
        if not texts:
            return RText()
        out = texts[0]
        for t in texts[1:]:
            out = out + sep + t
        return out

    @staticmethod
    def _combine_styles(base: str, overlay: str) -> str:
        fg: None | str = None
        bg: None | str = None
        attr: set[str] = set()

        for c in base:
            if c in FG.keys():
                fg = c
            elif c in BG.keys():
                bg = c
            elif c in ATTR.keys():
                attr.add(c)

        for c in overlay:
            if c in FG.keys():
                fg = c
            elif c in BG.keys():
                bg = c
            elif c in ATTR.keys():
                attr.add(c)

        return normalize_style("".join(sorted(attr)) + (fg or "") + (bg or ""))

    @staticmethod
    def parse(template: str, *args: Any) -> RText:
        runs: list[Run] = []
        buf = ""
        style = ""
        arg_i = 0
        i = 0

        def flush():
            nonlocal buf
            if buf:
                runs.append((style, buf))
                buf = ""

        while i < len(template):
            c = template[i]

            if c == "[":
                # escape [[
                if i + 1 < len(template) and template[i+1] == "[":
                    buf += "["
                    i += 2
                    continue

                j = template.find("]", i)
                if j == -1:
                    buf += c
                    i += 1
                    continue

                token = template[i+1:j]
                flush()

                # ---------- argumento ----------
                if token == "":
                    if arg_i < len(args):
                        arg = args[arg_i]
                        arg_i += 1

                        if isinstance(arg, RText):
                            # combina estilos
                            for s, t in arg.runs:
                                runs.append((RText._combine_styles(style, s), t))
                        elif isinstance(arg, tuple) and len(arg) == 2: # type: ignore
                            s, t = arg # type: ignore
                            runs.append((RText._combine_styles(style, s), t)) # type: ignore
                        else:
                            runs.append((style, str(arg))) # type: ignore

                # ---------- reset ----------
                elif token == ".":
                    style = ""

                # ---------- reset + style ----------
                elif token.startswith("."):
                    style = normalize_style(token[1:])

                # ---------- style ----------
                else:
                    style = RText._combine_styles(style, token)

                i = j + 1
                continue

            elif c == "]" and i + 1 < len(template) and template[i+1] == "]":
                buf += "]"
                i += 2
                continue

            else:
                buf += c
                i += 1

        if buf:
            runs.append((style, buf))

        return RText.from_runs(runs)

    def _merge(self, runs: Iterable[Run]) -> list[Run]:
        merged: list[Run] = []
        for style, text in runs:
            if not text:
                continue
            style = normalize_style(style)
            if merged and merged[-1][0] == style:
                merged[-1] = (style, merged[-1][1] + text)
            else:
                merged.append((style, text))
        return merged

    def _chars(self):
        for style, text in self.runs:
            for ch in text:
                yield ch, style

    def width(self) -> int:
        total: int = 0
        for _, text in self.runs:
            for ch in text:
                w: int = wcwidth(ch) # type: ignore
                if w > 0:
                    total += w # type: ignore
        return total # type: ignore

    def plain(self) -> str:
        return "".join(text for _, text in self.runs)

    def get_str(self) -> str:
        return self.plain()

    def render(self, mode: RenderMode | None = None) -> str:
        mode = mode or RenderConfig.mode
        if not RenderConfig.enabled or mode == RenderMode.PLAIN:
            return self.plain()
        if mode == RenderMode.DEBUG:
            return "".join(f"[{s}]{t}" for s, t in self.runs)
        out = ""
        for style, text in self.runs:
            if style:
                out += ansi(style) + text + ANSI["."]
            else:
                out += text
        return out

    def __str__(self) -> str:
        return self.render()

    def __len__(self) -> int:
        return len(self.plain())

    def len(self) -> int:
        return len(self)

    def __add__(self, other: "RText | str") -> RText:
        if isinstance(other, str):
            other = RText(other)
        return RText(runs=self.runs + other.runs)

    def __radd__(self, other: "RText | str") -> RText:
        if isinstance(other, str):
            other = RText(other)
        return RText(runs=other.runs + self.runs)
    
    def __getitem__(self, key: slice | int) -> RText:
        if isinstance(key, slice):
            start = key.start or 0
            end = key.stop if key.stop is not None else len(self)
            return self.slice(start, end)

        if key < 0:
            key += len(self)
        return self.slice(key, key + 1)

    def wrap(self, max_width: int) -> list["RText"]:
        lines: list[RText] = []
        current_runs: list[Run] = []
        current_width = 0

        def push_line():
            nonlocal current_runs
            if current_runs:
                lines.append(RText.from_runs(current_runs))
                current_runs = []

        for style, text in self.runs:
            for ch in text:
                if ch == "\n":
                    push_line()
                    current_width = 0
                    continue

                w = wcwidth(ch) # type: ignore
                if w < 0:
                    w = 0

                if current_width + w > max_width:
                    push_line()
                    current_width = 0

                if current_runs and current_runs[-1][0] == style:
                    current_runs[-1] = (style, current_runs[-1][1] + ch)
                else:
                    current_runs.append((style, ch))

                current_width += w # type: ignore

        push_line()
        return lines

    def truncate(self, max_width: int) -> "RText":
        if max_width <= 0:
            return RText()

        result: list[Run] = []
        current_width = 0

        for style, text in self.runs:
            part = ""

            for ch in text: 
                w = wcwidth(ch) # type: ignore
                if w < 0:
                    w = 0

                if current_width + w > max_width:
                    break

                part += ch
                current_width += w # type: ignore

            if part:
                if result and result[-1][0] == style:
                    result[-1] = (style, result[-1][1] + part)
                else:
                    result.append((style, part))

            if current_width >= max_width:
                break

        return RText.from_runs(result)

    def trim_end(self, width: int) -> "RText":
        return self.truncate(width)

    def slice(self, start: int = 0, end: int | None = None) -> RText:
        if end is None:
            end = len(self)
        if start < 0:
            start = 0
        if end <= start:
            return RText()

        result: list[Run] = []
        i = 0

        for style, text in self.runs:
            if i >= end:
                break

            part = ""
            for ch in text:
                if start <= i < end:
                    part += ch
                i += 1

            if part:
                if result and result[-1][0] == style:
                    result[-1] = (style, result[-1][1] + part)
                else:
                    result.append((style, part))

        return RText.from_runs(result)

    def upper(self) -> RText:
        return RText(runs=[(s, t.upper()) for s, t in self.runs])

    def lower(self) -> RText:
        return RText(runs=[(s, t.lower()) for s, t in self.runs])

    def replace(self, old: str, new: str | RText, style: str = "", count: int = -1) -> RText:
        if not old:
            return self

        if isinstance(new, str):
            new = RText(new, style)

        # explode em caracteres com estilo
        chars: list[tuple[str, str]] = []
        for s, t in self.runs:
            for c in t:
                chars.append((c, s))

        result: list[Run] = []
        i = 0
        replaced = 0
        n = len(old)

        def append_run(style: str, text: str):
            if not text:
                return
            if result and result[-1][0] == style:
                result[-1] = (style, result[-1][1] + text)
            else:
                result.append((style, text))

        while i < len(chars):
            # verifica match
            if (count == -1 or replaced < count) and \
            "".join(c for c, _ in chars[i:i+n]) == old:

                # adiciona novo texto
                for s, t in new.runs:
                    append_run(s, t)

                i += n
                replaced += 1
                continue

            c, s = chars[i]
            append_run(s, c)
            i += 1

        return RText.from_runs(result)

    def repeat(self, n: int) -> RText:
        return RText.concat(*([self] * n))

    def split(self, sep: str) -> list[RText]:
        parts: list[list[Run]] = [[]]
        sep_len = len(sep)

        i = 0

        # explode runs em (char, style)
        chars: list[tuple[str, str]] = []
        for style, text in self.runs:
            for c in text:
                chars.append((c, style))

        while i < len(chars):
            # verifica se começa com sep
            if "".join(c for c, _ in chars[i:i+sep_len]) == sep:
                parts.append([])
                i += sep_len
                continue

            c, style = chars[i]
            if parts[-1] and parts[-1][-1][0] == style:
                parts[-1][-1] = (style, parts[-1][-1][1] + c)
            else:
                parts[-1].append((style, c))

            i += 1

        return [RText.from_runs(p) for p in parts]

    def center(self, width: int, fill: RText | str = " ") -> RText:
        if isinstance(fill, str):
            fill = RText(fill)

        missing = width - len(self)
        if missing <= 0:
            return self

        left = missing // 2
        right = missing - left

        left_fill = RText.concat(*([fill] * left))
        right_fill = RText.concat(*([fill] * right))

        return left_fill + self + right_fill

    def fold_in(
        self,
        width: int,
        sep: RText | str = " ",
        left_border: RText | str = " ",
        right_border: RText | str = " ",
    ) -> RText:
        if isinstance(sep, str):
            sep = RText(sep)
        if isinstance(left_border, str):
            left_border = RText(left_border)
        if isinstance(right_border, str):
            right_border = RText(right_border)

        available = width - len(left_border) - len(right_border)
        content = self.truncate(max(0, available))
        missing = max(0, available - len(content))
        left = missing // 2
        right = missing - left
        return left_border + sep.repeat(left) + content + sep.repeat(right) + right_border

    def ljust(self, width: int, fill: RText | str = " ") -> RText:
        if isinstance(fill, str):
            fill = RText(fill)

        missing = width - len(self)
        if missing <= 0:
            return self

        filler = RText.concat(*([fill] * missing))
        return self + filler

    def rjust(self, width: int, fill: RText | str = " ") -> RText:
        if isinstance(fill, str):
            fill = RText(fill)

        missing = width - len(self)
        if missing <= 0:
            return self

        filler = RText.concat(*([fill] * missing))
        return filler + self

    def set_style(self, style: str) -> RText:
        return RText(runs=[(style, t) for _, t in self.runs])

    def add_style(self, style: str) -> RText:
        return RText(runs=[(s + style, t) for s, t in self.runs])

    def clear_style(self) -> RText:
        return RText(runs=[("", t) for _, t in self.runs])


class RBuffer:
    def __init__(self):
        self.runs: list[Run] = []

    def add(self, value: Any, style: str = ""):
        if value is None:
            return self

        # Text
        if isinstance(value, RText):
            for s, t in value.runs:
                self._add_run(s, t)
            return self

        # TextBuffer
        if isinstance(value, RBuffer):
            for s, t in value.runs:
                self._add_run(s, t)
            return self

        # Run tuple
        if isinstance(value, tuple) and len(value) == 2: # type: ignore
            s, t = value # type: ignore
            self._add_run(s, t) # type: ignore
            return self

        # Iterable[Run]
        if isinstance(value, list):
            for s, t in value: # type: ignore
                self._add_run(s, t) # type: ignore
            return self

        # string
        if isinstance(value, str):
            self._add_run(style, value)
            return self

        # fallback
        self._add_run(style, str(value)) # type: ignore
        return self

    def run(self, style: str, text: str):
        self._add_run(style, text)
        return self

    def extend(self, text: RText):
        for s, t in text.runs:
            self._add_run(s, t)
        return self

    def extend_runs(self, runs: Iterable[Run]):
        for s, t in runs:
            self._add_run(s, t)
        return self

    def _add_run(self, style: str, text: str):
        if not text:
            return
        style = normalize_style(style)
        if self.runs and self.runs[-1][0] == style:
            s, t = self.runs[-1]
            self.runs[-1] = (s, t + text)
        else:
            self.runs.append((style, text))

    def clear(self):
        self.runs.clear()
        return self

    def to_text(self) -> RText:
        return RText(runs=self.runs)

    def __iadd__(self, other: Any):
        return self.add(other)
    
    def __str__(self) -> str:
        return self.to_text().render()

if __name__ == "__main__":
    # Example usage
    t = RText.parse("Hello [] []!", ("r", "Red"), ("b", "Blue"))
    print(t)
    b = RBuffer()
    b.add("Hello ", "r").add("World", "R").add(" ").add(RText("oi", "bR"))
    # RenderConfig.mode = RenderMode.DEBUG
    
    # print(b.to_text().render(RenderMode.ANSI))
    # print(b.to_text().render(RenderMode.PLAIN))
    print(b.to_text().render())
    print(b.to_text().plain())
