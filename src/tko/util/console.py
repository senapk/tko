from __future__ import annotations

from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from io import StringIO, TextIOBase
from typing import Any, ClassVar
import sys
from tko.util.rt import RT
from tko.i18n import Msg, get_language
from enum import Enum

class Tee(TextIOBase):
    def __init__(self, *streams: TextIOBase) -> None:
        self.streams: tuple[TextIOBase, ...] = streams

    def write(self, data: str) -> int:
        for stream in self.streams:
            stream.write(data)

        return len(data)

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


type StreamLike = TextIOBase | Iterable[TextIOBase]

class SafeDict(dict[str, object]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"

class Console:
    stdout: ClassVar[TextIOBase] = sys.stdout  # type: ignore
    stderr: ClassVar[TextIOBase] = sys.stderr  # type: ignore

    @staticmethod
    def _normalize(stream: StreamLike) -> TextIOBase:
        if isinstance(stream, TextIOBase):
            return stream

        streams: tuple[TextIOBase, ...] = tuple(stream)

        if len(streams) == 1:
            return streams[0]

        return Tee(*streams)

    @staticmethod
    def format(
        *values: object,
        sep: str = " ",
        colors: bool = True,
        **format_kwargs: Any,
    ) -> str:
        rendered: list[str] = []
        language = get_language()
        for value in values:
            if isinstance(value, Msg):
                text = value.for_language(language)
            elif isinstance(value, Enum):
                text = str(value.value)
            else:
                text: str = str(value)

            if format_kwargs:
                text = text.format_map(SafeDict(format_kwargs))

            if colors and not isinstance(value, RT) and "[" in text:
                text = RT.parse(text).render()

            rendered.append(text)

        return sep.join(rendered)
    
    @staticmethod
    def print(
        *values: object,
        sep: str = " ",
        end: str = "\n",
        file: TextIOBase | None = None,
        flush: bool = False,
        err: bool = False,
        colors: bool = True,
        **format_kwargs: Any,
    ) -> None:
        rendered: str = Console.format(*values, sep=sep, colors=colors, **format_kwargs)

        stream: TextIOBase = file or (
            Console.stderr if err else Console.stdout
        )

        print(
            rendered,
            end=end,
            file=stream,
            flush=flush,
        )

    @staticmethod
    @contextmanager
    def redirect(
        *,
        stdout: StreamLike | None = None,
        stderr: StreamLike | None = None,
    ) -> Iterator[None]:
        previous_stdout = Console.stdout
        previous_stderr = Console.stderr

        try:
            if stdout is not None:
                Console.stdout = Console._normalize(stdout)

            if stderr is not None:
                Console.stderr = Console._normalize(stderr)

            yield

        finally:
            Console.stdout = previous_stdout
            Console.stderr = previous_stderr

    @staticmethod
    @contextmanager
    def capture(
        *,
        stderr: bool = False,
        tee: bool = False,
    ) -> Iterator[StringIO]:
        buffer = StringIO()

        stream: TextIOBase = buffer

        if tee:
            stream = Tee(
                Console.stderr if stderr else Console.stdout,
                buffer,
            )

        with Console.redirect(
            stderr=stream if stderr else None,
            stdout=stream if not stderr else None,
        ):
            yield buffer
