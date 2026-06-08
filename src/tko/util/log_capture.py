from collections.abc import Iterator
from loguru import logger

class LogCapture:
    def __init__(
        self,
        level: str = "DEBUG",
        format: str = "{message}",
    ) -> None:
        self.level = level
        self.format = format
        self.messages: list[str] = []
        self._sink_id: int | None = None

    def __enter__(self) -> "LogCapture":
        self._sink_id = logger.add(
            self.messages.append,
            level=self.level,
            format=self.format,
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> None: # type: ignore
        if self._sink_id is not None:
            logger.remove(self._sink_id)

    @property
    def text(self) -> str:
        return "\n".join(self.messages)

    def clear(self) -> None:
        self.messages.clear()

    def contains(self, text: str) -> bool:
        return text in self.text

    def assert_contains(self, text: str) -> None:
        assert text in self.text

    def assert_empty(self) -> None:
        assert self.messages == []

    def __iter__(self) -> Iterator[str]:
        return iter(self.messages)