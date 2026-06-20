from enum import Enum
from tko.util.rt import RT


from dataclasses import dataclass
from typing import Any


class RenderMode(Enum):
    COLOR = "color"
    PLAIN = "plain"
    FLAT = "flat"


@dataclass(frozen=True)
class Renderer:
    mode: RenderMode

    def render(self, value: Any) -> str:
        if not isinstance(value, RT):
            return str(value)

        match self.mode:
            case RenderMode.PLAIN:
                return value.plain()

            case RenderMode.COLOR:
                return value.ansi()

            case RenderMode.FLAT:
                return value.flat()

        raise ValueError(f"Invalid render mode: {self.mode}")