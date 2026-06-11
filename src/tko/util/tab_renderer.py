from tko.util.rt import RT

class TabRenderer:
    def render_button(self, info: str, test: bool) -> RT:
        bg = "G" if test else "X"
        return RT(" " + info + " ", bg)