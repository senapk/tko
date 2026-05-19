from tko.util.rtext import RText

class TabRenderer:
    def render_button(self, info: str, test: bool) -> RText:
        bg = "X" if test else ""
        return RText(" " + info + " ", bg)