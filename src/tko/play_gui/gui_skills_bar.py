from collections.abc import Callable

from tko.config.flags import Flags
from tko.game.game import Game
from tko.game.xp_resume import SkillResume
from tko.game.xp_display import truncate_total_xp
from tko.util.rt import RT
from tko.widget.bar_builder import BarBuilder
from tko.widget.colors import Colors


class GuiSkillsBar:
    """Progress line formatter consumed by the Textual skills panel."""

    def __init__(self, game: Game, colors: Colors, flags: Flags, remote: Callable[[], str]):
        self.game = game
        self.style = BarBuilder()
        self.colors = colors
        self.flags = flags
        self.remote = remote
        self.target_cut_factor = 1.2
        self.name_size = 8
        self.obtained_cut = 3
        self.target_cut = 3
        self.available_cut = 3
        self.overload = 1.1

    def get_entry_xp(self, resume: dict[str, SkillResume], skill: str, target: float, width: int) -> RT:
        value = resume[skill]
        title = f"{skill[:self.name_size]:<{self.name_size}}"
        obtained = f"{truncate_total_xp(value.obtained):>{self.obtained_cut}}"
        target100 = f"{truncate_total_xp(value.target100):>{self.target_cut}}"
        available = f"{truncate_total_xp(value.available):>{self.available_cut}}"
        label = RT(f"{title}:{obtained}/{target100}/{available}", "X")
        bar_size = width - (self.target_cut + self.available_cut + self.obtained_cut + self.name_size + 6)
        bar = self.style.build_progress_xp(value.obtained, value.target100, min(value.available, target), target, bar_size)
        return label + " " + bar
