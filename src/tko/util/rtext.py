from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Any
from wcwidth import wcwidth

Run = tuple[str, str]  # (style, text)

ANSI = {
    ".": "\033[0m",  # reset
    "*": "\033[1m",  # bold
    "_": "\033[4m",  # underline
    "/": "\033[3m",  # italic
    "~": "\033[7m",  # reverse
    "!": "\033[9m",  # strikethrough

    "k": "\033[30m",  # black
    "r": "\033[31m",  # red
    "g": "\033[32m",  # green
    "y": "\033[33m",  # yellow
    "b": "\033[34m",  # blue
    "m": "\033[35m",  # magenta
    "c": "\033[36m",  # cyan
    "w": "\033[37m",  # white

    "K": "\033[40m",  # black
    "R": "\033[41m",  # red
    "G": "\033[42m",  # green
    "Y": "\033[43m",  # yellow
    "B": "\033[44m",  # blue
    "M": "\033[45m",  # magenta
    "C": "\033[46m",  # cyan
    "W": "\033[47m",  # white
}

FG = set("krgybmcw")
BG = set("KRGYBMCW")
ATTR = set("*_/~!")


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
        fg = None
        bg = None
        attr: set[str] = set()

        for c in base:
            if c in FG:
                fg = c
            elif c in BG:
                bg = c
            elif c in ATTR:
                attr.add(c)

        for c in overlay:
            if c in FG:
                fg = c
            elif c in BG:
                bg = c
            elif c in ATTR:
                attr.add(c)

        result = ""
        if fg:
            result += fg
        if bg:
            result += bg
        if attr:
            result += "".join(sorted(attr))
        return result

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

            if c == "{":
                # escape {{
                if i + 1 < len(template) and template[i+1] == "{":
                    buf += "{"
                    i += 2
                    continue

                j = template.find("}", i)
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
                        else:
                            runs.append((style, str(arg)))

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

            elif c == "}" and i + 1 < len(template) and template[i+1] == "}":
                buf += "}"
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

    def __str__(self) -> str:
        out = ""
        for style, text in self.runs:
            if style:
                out += ansi(style) + text + ANSI["."]
            else:
                out += text
        return out

    def __len__(self) -> int:
        return len(self.plain())

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

    def slice(self, start: int, end: int) -> RText:
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

if __name__ == "__main__":
    # Example usage
    t = RText.parse("Hello {r}Red {}!", RText.run("b", "Blue"))
    b = RBuffer()
    b.add("Hello ", "r").add("World", "g").add(RText("oi", "R"))
    print(b.to_text())
