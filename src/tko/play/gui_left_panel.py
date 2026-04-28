from pathlib import Path

from tko.play.fmt import Fmt
from tko.play.frame import Frame
from tko.play.search import Search
from tko.play.tasktree import TaskTree
from tko.util.rtext import RText
from tko.util.symbols import Symbols
from typing import Callable

class GuiLeftPanel:

    def __init__(self, tree: TaskTree, search: Search, need_update_fn: Callable[[], bool]):
        self.tree = tree
        self.search = search
        self._need_update_fn = need_update_fn

    def make_search_text(self, size: int) -> RText:
        text = " Busca: " + self.tree.state.search + Symbols.cursor
        text = text.ljust(size)
        return RText(text)

    def show(self, frame: Frame) -> None:
        dy, dx = frame.get_inner()

        if self.search.search_mode:
            top = self.make_search_text(dx - 20)
        else:
            top = RText.format(" {} ", self.tree.repo.data.lang.upper())
        frame.set_header(top, "<", prefix="{", suffix="}")

        dirname: Path = self.tree.repo.paths.get_repo_root_dir()
        dirname_str = dirname.name.upper()

        text = RText.format(" {} ", dirname_str)
        if self._need_update_fn():
            text = (
                RText(" TKO DESATUALIZADO!", "r")
                + RText(" Atualize com: ", "y")
                + RText("pipx upgrade tko ", "g")
            )
        frame.set_footer(text, "<", prefix="{", suffix="}")
        frame.set_scrollbar(
            current_index=self.tree.state.scroll,
            text_length=len(self.tree.items),
            side="left",
        )
        frame.draw()

        sentences: list[RText] = self.tree.get_visible_sentences(dy)
        for y, sentence in enumerate(sentences):
            if sentence.len() > dx:
                sentence = sentence.trim_end(dx - 1) + RText("…", "r")
            frame.write(y, 0, sentence)
