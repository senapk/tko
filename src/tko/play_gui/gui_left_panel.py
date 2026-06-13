from pathlib import Path
from tko.widget.frame import Frame
from tko.play.search import Search
from tko.play_tree.task_tree import TaskTree
from tko.util.rt import RT
from tko.util.symbols import Symbols
from tko.i18n import Msg
from typing import Callable
from tko.game.tree_item import IsTreeItem
from tko.game.quest import Quest
from tko.game.task import Task


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

    def make_search_text(self, size: int) -> RT:
        text = str(_LeftPanelMsg.SEARCH) + self.tree.state.search + Symbols.cursor
        text = text.ljust(size)
        return RT(text)

    def _find_quest(self, sentences: list[tuple[RT, IsTreeItem]], quest: Quest) -> bool:
        for _, item in sentences:
            if item.basic.full_key == quest.basic.full_key:
                return True
        return False

    def show(self, frame: Frame) -> None:
        dy, dx = frame.get_inner()

        sentences: list[tuple[RT, IsTreeItem]] = self.tree.get_visible_sentences(dy)

        top = RT("")
        if self.search.search_mode:
            top = self.make_search_text(dx - 20)
        else:
            try:
                element = sentences[0][1]
                if isinstance(element, Task):
                    quest = self.tree.game.quests[element.quest_key]
                    if not self._find_quest(sentences, quest): 
                        top = self.tree.renderer.render_quest(quest, False)
            except IndexError:
                pass

        frame.set_header(top, "<")

        dirname: Path = self.tree.repo.paths.root_dir
        dirname_str = dirname.name.upper()

        text = RT.parse(" {}-{} ".format(dirname_str, self.tree.repo.data.lang.upper()))
        if self._need_update_fn():
            text = (
                RT(str(_LeftPanelMsg.OUTDATED), "r")
                + RT(str(_LeftPanelMsg.UPDATE_MESSAGE), "y")
                + RT(str(_LeftPanelMsg.UPDATE_COMMAND), "g")
            )
        frame.set_footer(text, "<", prefix="{", suffix="}")
        frame.set_scrollbar(
            current_index=self.tree.state.scroll,
            text_length=len(self.tree.items),
            side="left",
        )
        frame.draw()

        
        for y, (sentence, _) in enumerate(sentences):
            if len(sentence) > dx:
                sentence = sentence.trim_end(dx - 1) + RT("…", "r")
            frame.write(y, 0, sentence)
        