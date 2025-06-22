from tko.game.task import Task
from tko.game.quest import Quest
from tko.play.tasktree import TaskTree
from tko.play.flags import Flags
from tko.play.floating_manager import FloatingManager
from tko.play.input_manager import InputManager
from tko.play.keys import GuiKeys

class Search:
    def __init__(self, tree: TaskTree, fman: FloatingManager):
        self.tree = tree
        self.game = tree.game
        self.fman = fman
        self.search_mode: bool = False
        self.backup_expanded: list[str] = []
        self.backup_index_selected: str = ""
        self.backup_admin_mode: bool = False
        self.settings = tree.settings

    def toggle_search(self):
        self.search_mode = not self.search_mode
        if self.search_mode:
            self.backup_expanded = [v for v in self.tree.expanded]
            self.backup_index_selected = self.tree.selected_item
            self.backup_admin_mode = Flags.admin.is_true()
            self.tree.update_tree(admin_mode=True)
            self.tree.process_expand_all()
            self.tree.process_expand_all()
            
    def finish_search(self):
        if self.tree.selected_item == "":
            self.cancel_search()
            return

        self.search_mode = False
        self.tree.search_text = ""
        selected_key = self.tree.selected_item
        item = self.tree.all_items[selected_key]
        reachable = True
        if isinstance(item, Task):
            reachable = self.game.quests[item.quest_key].is_reachable()
        elif isinstance(item, Quest):
            reachable = item.is_reachable()
        if not reachable:
            Flags.admin.set_value("1")
        self.tree.update_tree(Flags.admin.is_true()) # usa o mode de antes e vê se acha
        self.tree.reload_sentences()
        
        self.tree.expanded = []
        unit = self.tree.all_items[selected_key]

        if isinstance(unit, Task):
            self.tree.expanded = [unit.cluster_key, unit.quest_key]
        elif isinstance(unit, Quest):
            self.tree.expanded = [unit.key, unit.cluster_key]
        self.tree.reload_sentences()

    # update index to match the first item that matches the search
    def update_index(self):
        _, first = self.tree.filter_by_search()
        self.tree.selected_item = first if first is not None else ""

    def cancel_search(self):
            self.search_mode = False
            self.tree.search_text = ""
            self.tree.expanded = [v for v in self.backup_expanded]
            self.tree.selected_item = self.backup_index_selected

    def process_search(self, key: int):
        if key == InputManager.esc:
            self.cancel_search()
        elif key == ord("\n"):
            self.finish_search()
        elif key == self.settings.app.get_key_up() or key == ord(GuiKeys.up) or key == ord(GuiKeys.up2):
            self.tree.move_up()
        elif key == self.settings.app.get_key_down() or key == ord(GuiKeys.down) or key == ord(GuiKeys.down2):
            self.tree.move_down()
        elif any([key == x for x in InputManager.backspace_list]):
            self.tree.search_text = self.tree.search_text[:-1]
            self.update_index()
        elif 32 <= key < 127:
            self.tree.search_text += chr(key).lower()
            self.update_index()
