from pathlib import Path

from tko.widget.frame import Frame
from tko.play.search import Search
from tko.play_tree.task_tree import TaskTree
from tko.util.rtext import RText
from tko.util.symbols import Symbols
from tko.i18n import Msg, t
from typing import Callable
from tko.game.tree_item import IsTreeItem


class _LeftPanelMsg:
    SEARCH = Msg(pt=" Busca: ", en=" Search: ")
    OUTDATED = Msg(pt=" TKO DESATUALIZADO!", en=" TKO OUTDATED!")
    UPDATE_MESSAGE = Msg(pt=" Atualize com: ", en=" Update with: ")
    UPDATE_COMMAND = Msg(pt="pipx upgrade tko ", en="pipx upgrade tko ")

class GuiLeftPanel:

    def __init__(self, tree: TaskTree, search: Search, need_update_fn: Callable[[], bool]):
        self.tree = tree
        self.search = search
        self._need_update_fn = need_update_fn

    def make_search_text(self, size: int) -> RText:
        text = t(_LeftPanelMsg.SEARCH) + self.tree.state.search + Symbols.cursor
        text = text.ljust(size)
        return RText(text)

    def show(self, frame: Frame) -> None:
        dy, dx = frame.get_inner()

        if self.search.search_mode:
            top = self.make_search_text(dx - 20)
        else:
            top = RText.format(" {} ", self.tree.repo.data.lang.upper())
        frame.set_header(top, "<", prefix="{", suffix="}")

        dirname: Path = self.tree.repo.paths.root_dir
        dirname_str = dirname.name.upper()

        text = RText.format(" {} ", dirname_str)
        if self._need_update_fn():
            text = (
                RText(t(_LeftPanelMsg.OUTDATED), "r")
                + RText(t(_LeftPanelMsg.UPDATE_MESSAGE), "y")
                + RText(t(_LeftPanelMsg.UPDATE_COMMAND), "g")
            )
        frame.set_footer(text, "<", prefix="{", suffix="}")
        frame.set_scrollbar(
            current_index=self.tree.state.scroll,
            text_length=len(self.tree.items),
            side="left",
        )
        frame.draw()

        sentences: list[tuple[RText, IsTreeItem]] = self.tree.get_visible_sentences(dy)
        for y, (sentence, _) in enumerate(sentences):
            if sentence.len() > dx:
                sentence = sentence.trim_end(dx - 1) + RText("…", "r")
            frame.write(y, 0, sentence)
