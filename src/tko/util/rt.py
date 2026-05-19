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


class ParseError(ValueError):
    pass


@dataclass(frozen=True)
class RT:
    runs: tuple[Run, ...] = ()

    def __init__(self, text: str = "", style: str = "", runs: Iterable[Run] | None = None):
        if runs is not None:
            object.__setattr__(self, "runs", tuple(self._merge(runs)))
        elif text:
            object.__setattr__(self, "runs", ((normalize_style(style), text),))
        else:
            object.__setattr__(self, "runs", ())

    @staticmethod
    def run(style: str, text: str) -> RT:
        return RT(text, style)

    @staticmethod
    def from_runs(runs: Iterable[Run]) -> RT:
        return RT(runs=runs)

    @staticmethod
    def decode_raw(data: str) -> RT:
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
            return RT(data)

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
        return RT.from_runs(runs)

    @staticmethod
    def concat(*texts: RT) -> RT:
        runs: list[Run] = []
        for t in texts:
            runs.extend(t.runs)
        return RT(runs=runs)

    @staticmethod
    def join(texts: Iterable[RT], sep: RT) -> RT:
        texts = list(texts)
        if not texts:
            return RT()
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
    def parse(template: str, *args: Any, **kwargs: Any) -> RT:
        runs: list[Run] = []
        buf = ""
        style = ""
        arg_i = 0
        i = 0

        ident_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

        def flush():
            nonlocal buf
            if buf:
                runs.append((style, buf))
                buf = ""

        def append_value(value: Any) -> None:
            if isinstance(value, RT):
                for s, t in value.runs:
                    runs.append((RT._combine_styles(style, s), t))
                return

            if isinstance(value, tuple) and len(value) == 2:  # type: ignore
                s = value[0]  # type: ignore
                t = value[1]  # type: ignore
                runs.append((RT._combine_styles(style, f"{s}"), f"{t}"))
                return

            runs.append((style, f"{value}"))

        def apply_style(value: Any, reset: bool = False) -> None:
            nonlocal style
            style_value = str(value)
            force_reset = False
            if style_value.startswith("."):
                force_reset = True
                style_value = style_value[1:]

            if reset or force_reset:
                style = normalize_style(style_value)
            else:
                style = RT._combine_styles(style, style_value)

        def parse_error(message: str) -> ParseError:
            return ParseError(f"{message} at pos {i}")

        while i < len(template):
            c = template[i]

            if c == "[":
                if i + 1 < len(template) and template[i+1] == "[":
                    buf += "["
                    i += 2
                    continue

                j = template.find("]", i)
                if j == -1:
                    raise parse_error("missing closing ]")

                token = template[i+1:j]
                flush()

                if token == "." or token == "":
                    style = ""
                elif token.startswith("."):
                    style = normalize_style(token[1:])
                else:
                    style = RT._combine_styles(style, token)

                i = j + 1
                continue

            if c == "<":
                if i + 1 < len(template) and template[i + 1] == "<":
                    buf += "<"
                    i += 2
                    continue

                j = template.find(">", i)
                if j == -1:
                    raise parse_error("missing closing >")

                token = template[i + 1:j]
                flush()

                if token == "":
                    if arg_i >= len(args):
                        raise parse_error("missing positional value for <>")
                    append_value(args[arg_i])
                    arg_i += 1
                else:
                    if ident_re.match(token):
                        if token not in kwargs:
                            raise parse_error(f"missing named value: {token}")
                        append_value(kwargs[token])
                    else:
                        # Non-identifier payload is treated as literal text.
                        buf += f"<{token}>"

                i = j + 1
                continue

            if c == "(":
                if i + 1 < len(template) and template[i + 1] == "(":
                    buf += "("
                    i += 2
                    continue

                j = template.find(")", i)
                if j == -1:
                    raise parse_error("missing closing )")

                token = template[i + 1:j]
                flush()

                if token == "":
                    if arg_i >= len(args):
                        raise parse_error("missing positional style for ()")
                    apply_style(args[arg_i], reset=False)
                    arg_i += 1
                elif token == ".":
                    style = ""
                elif token.startswith("."):
                    key = token[1:]
                    if ident_re.match(key):
                        if key not in kwargs:
                            raise parse_error(f"missing named style: {key}")
                        apply_style(kwargs[key], reset=True)
                    else:
                        buf += f"({token})"
                else:
                    if ident_re.match(token):
                        if token not in kwargs:
                            raise parse_error(f"missing named style: {token}")
                        apply_style(kwargs[token], reset=False)
                    else:
                        buf += f"({token})"

                i = j + 1
                continue

            elif c == "]" and i + 1 < len(template) and template[i+1] == "]":
                buf += "]"
                i += 2
                continue

            elif c == ">" and i + 1 < len(template) and template[i + 1] == ">":
                buf += ">"
                i += 2
                continue

            elif c == ")" and i + 1 < len(template) and template[i + 1] == ")":
                buf += ")"
                i += 2
                continue

            else:
                buf += c
                i += 1

        if buf:
            runs.append((style, buf))

        return RT.from_runs(runs)

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

    def __add__(self, other: "RT | str") -> RT:
        if isinstance(other, str):
            other = RT(other)
        return RT(runs=self.runs + other.runs)

    def __radd__(self, other: "RT | str") -> RT:
        if isinstance(other, str):
            other = RT(other)
        return RT(runs=other.runs + self.runs)
    
    def __getitem__(self, key: slice | int) -> RT:
        if isinstance(key, slice):
            start = key.start or 0
            end = key.stop if key.stop is not None else len(self)
            return self.slice(start, end)

        if key < 0:
            key += len(self)
        return self.slice(key, key + 1)

    def wrap(self, max_width: int) -> list["RT"]:
        lines: list[RT] = []
        current_runs: list[Run] = []
        current_width = 0

        def push_line():
            nonlocal current_runs
            if current_runs:
                lines.append(RT.from_runs(current_runs))
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

    def truncate(self, max_width: int) -> "RT":
        if max_width <= 0:
            return RT()

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

        return RT.from_runs(result)

    def trim_end(self, width: int) -> "RT":
        return self.truncate(width)

    def slice(self, start: int = 0, end: int | None = None) -> RT:
        if end is None:
            end = len(self)
        if start < 0:
            start = 0
        if end <= start:
            return RT()

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

        return RT.from_runs(result)

    def upper(self) -> RT:
        return RT(runs=[(s, t.upper()) for s, t in self.runs])

    def lower(self) -> RT:
        return RT(runs=[(s, t.lower()) for s, t in self.runs])

    def replace(self, old: str, new: str | RT, style: str = "", count: int = -1) -> RT:
        if not old:
            return self

        if isinstance(new, str):
            new = RT(new, style)

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

        return RT.from_runs(result)

    def repeat(self, n: int) -> RT:
        return RT.concat(*([self] * n))

    def split(self, sep: str) -> list[RT]:
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

        return [RT.from_runs(p) for p in parts]

    def center(self, width: int, fill: RT | str = " ") -> RT:
        if isinstance(fill, str):
            fill = RT(fill)

        missing = width - len(self)
        if missing <= 0:
            return self

        left = missing // 2
        right = missing - left

        left_fill = RT.concat(*([fill] * left))
        right_fill = RT.concat(*([fill] * right))

        return left_fill + self + right_fill

    def fold_in(
        self,
        width: int,
        sep: RT | str = " ",
        left_border: RT | str = " ",
        right_border: RT | str = " ",
    ) -> RT:
        if isinstance(sep, str):
            sep = RT(sep)
        if isinstance(left_border, str):
            left_border = RT(left_border)
        if isinstance(right_border, str):
            right_border = RT(right_border)

        available = width - len(left_border) - len(right_border)
        content = self.truncate(max(0, available))
        missing = max(0, available - len(content))
        left = missing // 2
        right = missing - left
        return left_border + sep.repeat(left) + content + sep.repeat(right) + right_border

    def ljust(self, width: int, fill: RT | str = " ") -> RT:
        if isinstance(fill, str):
            fill = RT(fill)

        missing = width - len(self)
        if missing <= 0:
            return self

        filler = RT.concat(*([fill] * missing))
        return self + filler

    def rjust(self, width: int, fill: RT | str = " ") -> RT:
        if isinstance(fill, str):
            fill = RT(fill)

        missing = width - len(self)
        if missing <= 0:
            return self

        filler = RT.concat(*([fill] * missing))
        return filler + self

    def set_style(self, style: str) -> RT:
        return RT(runs=[(style, t) for _, t in self.runs])

    def add_style(self, style: str) -> RT:
        return RT(runs=[(s + style, t) for s, t in self.runs])

    def clear_style(self) -> RT:
        return RT(runs=[("", t) for _, t in self.runs])


class RBuffer:
    def __init__(self):
        self.runs: list[Run] = []

    def add(self, value: Any, style: str = ""):
        if value is None:
            return self

        # Text
        if isinstance(value, RT):
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

    def extend(self, text: RT):
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

    def to_text(self) -> RT:
        return RT(runs=self.runs)

    def __iadd__(self, other: Any):
        return self.add(other)
    
    def __str__(self) -> str:
        return self.to_text().render()

if __name__ == "__main__":
    # Example usage
    t = RT.parse("(name)Hello <who>(.)!", who=("r", "Red"), name="b")
    print(t)
    b = RBuffer()
    b.add("Hello ", "r").add("World", "R").add(" ").add(RT("oi", "bR"))
    # RenderConfig.mode = RenderMode.DEBUG
    
    # print(b.to_text().render(RenderMode.ANSI))
    # print(b.to_text().render(RenderMode.PLAIN))
    print(b.to_text().render())
    print(b.to_text().plain())
