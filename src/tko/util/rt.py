from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Iterable
from wcwidth import wcwidth
import re
from tko.util.text_style import TextStyle, ANSI_RESET

Run = tuple[TextStyle, str]  # (style, text)


class ParseError(ValueError):
    pass

class SafeDict(dict[str, object]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _append_run(runs: list[Run], style: TextStyle, text: str) -> None:
    if not text:
        return
    if runs and runs[-1][0] == style:
        s, t = runs[-1]
        runs[-1] = (s, t + text)
    else:
        runs.append((style, text))

def _merge(runs: Iterable[Run]) -> list[Run]:
    merged: list[Run] = []
    for style, text in runs:
        _append_run(merged, style, text)
    return merged

def _char_width(ch: str) -> int:
    w = wcwidth(ch)
    return max(w, 0)

class RunBuilder:
    def __init__(self) -> None:
        self._runs: list[Run] = []

    def append(self, style: TextStyle, text: str) -> None:
        _append_run(self._runs, style, text)

    def extend(self, runs: Iterable[Run]) -> None:
        for style, text in runs:
            _append_run(self._runs, style, text)

    @property
    def empty(self) -> bool:
        return not self._runs

    def clear(self) -> None:
        self._runs.clear()

    def snapshot(self) -> list[Run]:
        return self._runs.copy()

    def __iter__(self):
        return iter(self._runs)

    def copy(self) -> RunBuilder:
        builder = RunBuilder()
        builder._runs = self._runs.copy()
        return builder


@dataclass(frozen=True)
class RT:
    """
    Contrato funcional do RT.

    Objetivo:
    - Representar texto rico como uma sequência imutável de runs (style, text).
    - Oferecer operações previsíveis de composição, fatia, alinhamento e renderização.

    Invariantes:
    - A estrutura interna é imutável (dataclass frozen).
    - Runs com texto vazio são descartados durante normalização/merge.
    - Runs adjacentes com o mesmo estilo são mesclados.
    - Todo estilo é normalizado pela class Style.

    Modelo de estilo:
    - O estilo corrente do parse é cumulativo por overlay.
    - [] faz pop do estilo atual, retornando ao anterior.
    - [x] aplica overlay do estilo literal x no estilo corrente.
    - [.x] faz reset + apply do estilo literal x.

    Contrato de parse:
    - Delimitadores são "[ ]" (controle de estilo).
    - "[[" e "]]" são escapes literais.
    - Erros de fechamento e variáveis ausentes lançam ParseError.

    Renderização:
    - ANSI: aplica códigos de estilo em cada run com reset ao fim do run.
    - PLAIN: retorna apenas o conteúdo textual.
    - FLAT: expõe runs no formato [style]text[].
    """
    runs: tuple[Run, ...] = ()
    ANSI_RE = re.compile(r"\033\[([0-9;]*)m")

    def __init__(self, text: str = "", style: str = "", runs: Iterable[Run] | None = None):
        if runs is not None:
            object.__setattr__(self, "runs", tuple(_merge(runs)))
        elif text:
            object.__setattr__(self, "runs", ((TextStyle.parse(style), text),))
        else:
            object.__setattr__(self, "runs", ())

    @staticmethod
    def run(style: str, text: str) -> RT:
        return RT(text, style)

    @staticmethod
    def from_runs(runs: Iterable[Run]) -> RT:
        return RT(runs=runs)

    @staticmethod
    def from_ansi(data: str) -> RT:
        rb = RunBuilder()

        style = TextStyle()

        last = 0

        for match in RT.ANSI_RE.finditer(data):
            start, end = match.span()

            if start > last:
                rb.append(
                    style,
                    data[last:start],
                )

            raw = match.group(1)

            codes = raw.split(";") if raw else ["0"]

            style = TextStyle.from_ansi_codes(
                codes,
                style,
            )

            last = end

        if last < len(data):
            rb.append(style, data[last:])

        return RT.from_runs(rb)


    @staticmethod
    def parse(template: str) -> RT:
        """
        Gramática simplificada do parser RT.

        Objetivo:
        - Converter markup inline baseado em [style] em uma sequência
        imutável de runs (style, text).

        Controle de estilo:
        - [style]   faz push de um novo estilo combinado com o atual.
        - [.style] faz reset + apply do estilo literal, ignorando o atual.
        - []        faz pop do estilo atual.
        - [[        escape literal para "[".
        - ]]        escape literal para "]".

        Regras:
        - Os estilos são mantidos em uma pilha.
        - Cada [style] faz overlay sobre o topo atual da pilha.
        - [] restaura o estilo anterior.
        - Cores foreground/background substituem anteriores.
        - Attributes (*, _, etc.) são acumulativos.

        Exemplos:
        - [r]erro[]
        - [R]fundo vermelho [g]verde sobre vermelho[] vermelho[]
        - [r*]erro em negrito[]
        - [.r]erro em vermelho[]
        - [[texto]] -> [texto]

        Regras de erro:
        - Tags "[" sem fechamento "]" geram ParseError.
        - [] em pilha vazia é ignorado.

        Renderização:
        - O parser apenas produz runs estruturados.
        - A renderização ANSI/plain/flat é responsabilidade de render().
        """
        run_builder = RunBuilder()
        buf = ""
        i = 0

        style_stack: list[TextStyle] = [TextStyle()]

        def flush() -> None:
            nonlocal buf

            if buf:
                run_builder.append(style_stack[-1], buf)
                buf = ""

        def parse_error(message: str) -> ParseError:
            return ParseError(f"{message} at pos {i}")

        while i < len(template):
            c = template[i]

            # Escapes
            if c == "[" and i + 1 < len(template) and template[i + 1] == "[":
                buf += "["
                i += 2
                continue

            if c == "]" and i + 1 < len(template) and template[i + 1] == "]":
                buf += "]"
                i += 2
                continue

            # Style tag
            if c == "[":
                j = template.find("]", i)

                if j == -1:
                    raise parse_error("missing closing ]")

                token = template[i + 1:j]

                flush()

                # Pop
                if token == "":
                    if len(style_stack) > 1:
                        style_stack.pop()

                    style = style_stack[-1]

                elif token.startswith("."):
                    style = TextStyle.parse(token[1:])
                    style_stack.append(style)

                # Push
                else:
                    style = style_stack[-1].overlay(token)
                    style_stack.append(style)

                i = j + 1
                continue

            # Normal text
            buf += c
            i += 1

        flush()

        return RT.from_runs(run_builder)

    def plain(self) -> str:
        return "".join(text for _, text in self.runs)
    
    def flat(self) -> str:
        output: list[str] = []
        for s, t in self.runs:
            if not s.is_plain():
                output.append(f"[{s}]{t}[]")
            else:
                output.append(t)
        return "".join(output)
    
    def ansi(self) -> str:
        out = ""
        for style, text in self.runs:
            if style:
                out += style.ansi() + text + ANSI_RESET
            else:
                out += text
        return out
    
    def __iter__(self) -> Iterator[Run]:
        return iter(self.runs)
    
    def __str__(self) -> str:
        return self.flat()

    def __len__(self) -> int:
        return sum(_char_width(ch) for ch, _ in self.iter_chars())
    
    def set_style(self, style: str | TextStyle) -> RT:
        if isinstance(style, str):
            style = TextStyle.parse(style)

        return RT.from_runs(
            runs=[(style, t) for _, t in self.runs]
        )
    
    def add_style(self, style: str | TextStyle) -> RT:
        if isinstance(style, str):
            style = TextStyle.parse(style)

        return RT.from_runs(
            runs=[
                (s.overlay(style), t)
                for s, t in self.runs
            ]
        )

    def strip_style(self) -> RT:
        return RT.from_runs(
            runs=[(TextStyle(), t) for _, t in self.runs]
        )


    def __add__(self, other: RT | str) -> RT:
        if isinstance(other, str):
            other = RT(other)
        return RT(runs=self.runs + other.runs)

    def __radd__(self, other: RT | str) -> RT:
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
    
    def iter_chars(self) -> Iterator[tuple[str, TextStyle]]:
        for style, text in self.runs:
            for ch in text:
                yield ch, style

    # Align and truncation methods

    @staticmethod
    def join(texts: Iterable[RT], sep: RT | str = "") -> RT:
        if isinstance(sep, str):
            sep = RT(sep)
        builder = RunBuilder()
        first = True
        for text in texts:
            if not first:
                builder.extend(sep.runs)
            builder.extend(text.runs)
            first = False
        return RT.from_runs(builder)

    def wrap(self, max_width: int) -> list[RT]:
        """
        Breaks the RT into multiple lines, each with a maximum width of max_width.
        """
        lines: list[RT] = []
        rb = RunBuilder()
        current_width = 0

        def push_line():
            nonlocal rb
            if not rb.empty:
                lines.append(RT.from_runs(rb))
                rb = RunBuilder()

        for ch, style in self.iter_chars():
            if ch == "\n":
                push_line()
                current_width = 0
                continue

            w = _char_width(ch)

            if current_width + w > max_width:
                push_line()
                current_width = 0
            rb.append(style, ch)
            current_width += w # type: ignore

        push_line()
        return lines

    def truncate(self, max_width: int) -> RT:
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
        chars: list[tuple[str, TextStyle]] = []
        for s, t in self.runs:
            for c in t:
                chars.append((c, s))

        result: list[Run] = []
        i = 0
        replaced = 0
        n = len(old)

        def append_run(style: TextStyle, text: str):
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
        if n <= 0:
            return RT()

        return RT.from_runs(self.runs * n)

    def split(self, sep: str) -> list[RT]:
        parts: list[list[Run]] = [[]]
        sep_len = len(sep)

        i = 0

        # explode runs em (char, style)
        chars: list[tuple[str, TextStyle]] = []
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

    def splitlines(self) -> list[RT]:
        return self.split("\n")

    def center(self, width: int, fill: RT | str = " ") -> RT:
        if isinstance(fill, str):
            fill = RT(fill)
        if len(fill) != 1:
            raise ValueError("fill must be a single character")

        missing = width - len(self)

        if missing <= 0:
            return self

        left = missing // 2
        right = missing - left

        return ( fill.repeat(left) + self + fill.repeat(right) )

    def center_in(
        self,
        width: int,
        sep: RT | str = " ",
        left_border: RT | str = " ",
        right_border: RT | str = " ",
    ) -> RT:
        if isinstance(sep, str):
            sep = RT(sep)
        if len(sep) != 1:
            raise ValueError("sep must be a single character")
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
        if len(fill) != 1:
            raise ValueError("fill must be a single character")

        missing = width - len(self)
        if missing <= 0:
            return self

        filler = fill.repeat(missing)
        return self + filler

    def rjust(self, width: int, fill: RT | str = " ") -> RT:
        if isinstance(fill, str):
            fill = RT(fill)
        if len(fill) != 1:
            raise ValueError("fill must be a single character")

        missing = width - len(self)
        if missing <= 0:
            return self

        filler = fill.repeat(missing)
        return filler + self

if __name__ == "__main__":
    print(RT.parse("[R]red [Kg]green [b]blue[][]red[]"))