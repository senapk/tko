from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from enum import Enum
from io import StringIO
from typing import Any, ClassVar, Protocol, TextIO

import sys

from tko.util.rt import RT


class RenderMode(Enum):
    ANSI = "ansi"
    PLAIN = "plain"
    FLAT = "flat"


class Renderer:
    @staticmethod
    def render(
        value: Any,
        mode: RenderMode,
    ) -> str:
        if not isinstance(value, RT):
            return str(value)

        match mode:
            case RenderMode.PLAIN:
                return value.plain()

            case RenderMode.ANSI:
                return value.ansi()

            case RenderMode.FLAT:
                return value.flat()

        raise ValueError(f"Invalid render mode: {mode}")


class Writer(Protocol):
    def write(
        self,
        *values: RT,
        sep: str = " ",
        end: str = "\n",
    ) -> None: ...

    def flush(self) -> None: ...


class PrintWriter:
    def __init__(
        self,
        file: TextIO,
        mode: RenderMode = RenderMode.ANSI,
    ) -> None:
        self.file = file
        self.mode = mode

    def write(
        self,
        *values: RT,
        sep: str = " ",
        end: str = "\n",
    ) -> None:
        self.file.write(
            sep.join(
                Renderer.render(
                    value,
                    self.mode,
                )
                for value in values
            )
        )

        self.file.write(end)

    def flush(self) -> None:
        self.file.flush()


class CaptureWriter:
    def __init__(
        self,
        mode: RenderMode = RenderMode.PLAIN,
    ) -> None:
        self.buffer = StringIO()
        self.mode = mode

    def write(
        self,
        *values: RT,
        sep: str = " ",
        end: str = "\n",
    ) -> None:
        self.buffer.write(
            sep.join(
                Renderer.render(
                    value,
                    self.mode,
                )
                for value in values
            )
        )

        self.buffer.write(end)

    def flush(self) -> None:
        pass

    def getvalue(self) -> str:
        return self.buffer.getvalue()


class Console:
    stdout: ClassVar[Writer] = PrintWriter(
        sys.stdout,
        RenderMode.ANSI,
    )

    stderr: ClassVar[Writer] = PrintWriter(
        sys.stderr,
        RenderMode.ANSI,
    )

    @staticmethod
    def rt(value: Any) -> RT:
        if isinstance(value, RT):
            return value

        return RT(str(value))

    @staticmethod
    def _write(
        stream: Writer,
        *values: Any,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        stream.write(
            *(Console.rt(value) for value in values),
            sep=sep,
            end=end,
        )

        if flush:
            stream.flush()

    @staticmethod
    def print(
        *values: Any,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        Console._write(
            Console.stdout,
            *values,
            sep=sep,
            end=end,
            flush=flush,
        )

    @staticmethod
    def error(
        *values: Any,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        Console._write(
            Console.stderr,
            *values,
            sep=sep,
            end=end,
            flush=flush,
        )

    @staticmethod
    @contextmanager
    def redirect(
        *,
        stdout: Writer | None = None,
        stderr: Writer | None = None,
    ) -> Iterator[None]:
        previous_stdout = Console.stdout
        previous_stderr = Console.stderr

        try:
            if stdout is not None:
                Console.stdout = stdout

            if stderr is not None:
                Console.stderr = stderr

            yield

        finally:
            Console.stdout = previous_stdout
            Console.stderr = previous_stderr

    @staticmethod
    @contextmanager
    def capture(
        *,
        stderr: bool = False,
        mode: RenderMode = RenderMode.PLAIN,
    ) -> Iterator[CaptureWriter]:
        capture = CaptureWriter(mode)

        with Console.redirect(
            stderr=capture if stderr else None,
            stdout=capture if not stderr else None,
        ):
            yield capture