from tko.floating.floating import FloatingABC
from tko.floating.floating import Floating
from tko.util.rt import RT
from tko.util.console import RenderMode


class FloatingManager:
    def __init__(self):
        self.input_layer: list[FloatingABC] = []

    def add_floating(self, floating: FloatingABC):
        self.input_layer.append(floating)

    def get_top(self) -> FloatingABC | None:
        if len(self.input_layer) == 0:
            return None
        return self.input_layer[0]

    def draw_warnings(self):
        if len(self.input_layer) > 0 and self.input_layer[0].is_enable():
            self.input_layer[0].draw()

    def has_floatings(self) -> bool:
        while len(self.input_layer) > 0 and not self.input_layer[0].is_enable():
            self.input_layer = self.input_layer[1:]
        return len(self.input_layer) > 0 and self.input_layer[0].is_enable()

    def draw(self) -> None:
        self.input_layer[0].draw()

    def process_input(self, key: int) -> int:
        return self.input_layer[0].process_input(key)


class FloatingWriter:
    def __init__(self, fman: FloatingManager, align: str, mode: RenderMode = RenderMode.COLOR) -> None:
        self.fman = fman
        self.mode = mode
        self.align = align

    def write(self, *values: RT, sep: str = " ", end: str = "\n") -> None:
        content = RT(sep).join([value for value in values])
        content_list = content.splitlines()
        
        self.fman.add_floating(
            Floating().set_warning().set_frame_align(self.align).set_content_rt(content_list).set_countdown(Floating.Time.FAST)
        )

    def flush(self) -> None:
        pass