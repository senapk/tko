from tko.play_tree.task_tree import TaskTree
from tko.floating.floating_manager import FloatingManager
from tko.play.search_session_service import SearchSessionService
from tko.play.search_service import SearchService
import curses

class Search:
    def __init__(self, tree: TaskTree, fman: FloatingManager):
        self.tree = tree
        self.game = tree.game
        self.fman = fman
        self.repo = tree.repo
        self.search_mode: bool = False
        self.session = SearchSessionService(tree)
        self.service = SearchService(tree)
        self.settings = tree.settings

    def toggle_search(self):
        if not self.search_mode:
            self.session.start()
        self.search_mode = not self.search_mode
            
    def finish_search(self):
        if self.tree.state.selected == "":
            self.cancel_search()
            return

        self.search_mode = False
        self.tree.state.search = ""
        selected = self.tree.state.selected
        if not self.service.finish(selected, self.session.inbox_in_beggining):
            # The filtered selection may become stale after state transitions.
            self.cancel_search()
        return

    # update index to match the first item that matches the search
    def update_index(self):
        self.service.update_selected_from_search()

    def cancel_search(self):
        self.search_mode = False
        self.session.cancel()

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
