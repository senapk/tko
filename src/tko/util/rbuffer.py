from tko.util.rt import RT, Run
from tko.util.rt import RunBuilder
from tko.util.rt_style import RTStyle


from typing import Any, Iterable


class RBuffer:
    def __init__(self):
        self.builder = RunBuilder()

    def add(self, value: Any, style: str = ""):
        if value is None:
            return self

        if isinstance(value, RT):
            for s, t in value.runs:
                self.builder.append(s, t)
            return self

        if isinstance(value, RBuffer):
            for s, t in value.builder:
                self.builder.append(s, t)
            return self

        # string
        if isinstance(value, str):
            self.add_run(style, value)
            return self

        # fallback
        self.add_run(style, str(value))
        return self

    def run(self, style: RTStyle, text: str):
        self.builder.append(style, text)
        return self

    def extend(self, runs: Iterable[Run]):
        for s, t in runs:
            self.builder.append(s, t)
        return self

    def add_run(self, style: str, text: str):
        if not text:
            return
        self.builder.append(RTStyle.parse(style), text)

    def clear(self):
        self.builder.clear()
        return self

    def to_rt(self) -> RT:
        return RT.from_runs(self.builder)

    def __iadd__(self, other: Any):
        return self.add(other)

    def __str__(self) -> str:
        return self.to_rt().render()