from tko.play.floating import Floating

class FloatingManager:
    def __init__(self):
        self.input_layer: list[Floating] = []

    def add_input(self, floating: Floating):
        self.input_layer.append(floating)

    def draw_warnings(self):
        if len(self.input_layer) > 0 and self.input_layer[0].is_enable():
            self.input_layer[0].draw()

    def has_floating(self) -> bool:
        while len(self.input_layer) > 0 and not self.input_layer[0].is_enable():
            self.input_layer = self.input_layer[1:]
        return len(self.input_layer) > 0 and self.input_layer[0].is_enable()

    def draw(self) -> None:
        self.input_layer[0].draw()

    def process_input(self, key: int) -> int:
        return self.input_layer[0].process_input(key)
