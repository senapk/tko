from tko.util.rt import RT

class TabRenderer:
    def render_button(self, info: str, test: bool) -> RT:
        bg = "X" if test else ""
        return RT(" " + info + " ", bg)