from tko.game.task import Task
from tko.game.quest import Quest
from tko.play.tasktree import TaskTree
from tko.play.floating_manager import FloatingManager
import curses

class Search:
    def __init__(self, tree: TaskTree, fman: FloatingManager):
        self.tree = tree
        self.game = tree.game
        self.fman = fman
        self.repo = tree.repo
        self.search_mode: bool = False
        self.backup_expanded: list[str] = []
        self.backup_index_selected: str = ""
        self.backup_inbox_op = ""
        self.settings = tree.settings

    def toggle_search(self):
        if not self.search_mode:
            self.backup_expanded = [v for v in self.tree.state.expanded]
            self.backup_index_selected = self.tree.state.selected
            self.tree.update(force_view_all=True)
            self.tree.expand_all()
            self.inbox_in_beggining: bool = self.repo.flags.task_view_mode.is_inbox()
            self.repo.flags.task_view_mode.set_view_all()    
        self.search_mode = not self.search_mode
            
    def finish_search(self):
        if self.tree.state.selected == "":
            self.cancel_search()
            return

        self.search_mode = False
        self.tree.state.search = ""
        selected = self.tree.state.selected
        item = self.tree.get_selected_throw()
        if self.inbox_in_beggining: # try to found item using inbox mode
            self.tree.update(force_view_all=False)
            reachable = True
            if isinstance(item, Task):
                reachable = self.game.quests[item.quest_key].is_reachable()
            elif isinstance(item, Quest):
                reachable = item.is_reachable()
            if not reachable:
                self.repo.flags.task_view_mode.set_view_all()
            else:
                self.repo.flags.task_view_mode.set_view_inbox()

        self.tree.update()
        self.tree.state.selected = selected
        self.tree.state.expanded = set()
        unit = self.tree.get_selected_throw()

        if isinstance(unit, Task):
            self.tree.state.expanded = {unit.remote_name, unit.quest_key}
        elif isinstance(unit, Quest):
            self.tree.state.expanded = {unit.get_full_key(), unit.remote_name}

    # update index to match the first item that matches the search
    def update_index(self):
        _, first = self.tree.filter_by_search()
        self.tree.state.selected = first if first is not None else ""

    def cancel_search(self):
            self.search_mode = False
            self.tree.state.search = ""
            self.tree.state.expanded = {v for v in self.backup_expanded}
            self.tree.state.selected = self.backup_index_selected

    def process_search(self, key: int):
        if key == curses.KEY_EXIT:
            self.cancel_search()
        elif key == ord("\n"):
            self.finish_search()
        elif key == curses.KEY_UP:
            self.tree.move_up()
        elif key == curses.KEY_DOWN:
            self.tree.move_down()
        elif key == curses.KEY_LEFT or key == curses.KEY_BACKSPACE:
            self.tree.state.search = self.tree.state.search[:-1]
            self.update_index()
        elif 32 <= key < 127:
            self.tree.state.search += chr(key).lower()
            self.update_index()
