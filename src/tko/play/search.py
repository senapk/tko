from tko.game.task import Task
from tko.game.quest import Quest
from tko.play.tasktree import TaskTree
from tko.play.flags import Flags
from tko.play.floating import Floating
from tko.play.floating_manager import FloatingManager

import curses
from typing import List

class Search:
    def __init__(self, tree: TaskTree, fman: FloatingManager):
        self.tree = tree
        self.game = tree.game
        self.fman = fman
        self.search_mode: bool = False
        self.backup_expanded: List[str] = []
        self.backup_index_selected = 0
        self.backup_admin_mode = False

    def toggle_search(self):
        self.search_mode = not self.search_mode
        if self.search_mode:
            self.backup_expanded = [v for v in self.tree.expanded]
            self.backup_index_selected = self.tree.index_selected
            self.backup_admin_mode = Flags.admin.is_true()
            self.tree.update_tree(admin_mode=True)
            self.tree.process_expand()
            self.tree.process_expand()
            self.fman.add_input(Floating(">v").warning().put_text("Digite o texto\nVavegue até o elemnto desejado\ne aperte Enter"))
    
    def finish_search(self):
        self.search_mode = False
        unit = self.tree.get_selected()
        self.tree.index_selected = 0
        self.tree.search_text = ""
        if self.backup_admin_mode == False:
            self.tree.update_tree(admin_mode=False)
        self.tree.reload_sentences()
    
        found = False
        for i, item in enumerate(self.tree.items):
            if item.obj == unit:
                self.tree.index_selected = i
                found = True
                break

        if not found:
            self.fman.add_input(Floating(">v").warning().put_text("Elemento não acessível no modo normal.\nEntrando no modo Admin\npara habilitar acesso"))
            Flags.admin.toggle()
            self.tree.update_tree(True)
            self.tree.reload_sentences()
        
        self.tree.process_collapse()
        self.tree.process_collapse()

        if isinstance(unit, Task):
            for cluster_key in self.game.available_clusters:
                cluster = self.game.clusters[cluster_key]
                for quest in cluster.quests:
                    for task in quest.get_tasks():
                        if task == unit:
                            self.tree.expanded = [cluster.key, quest.key]
        elif isinstance(unit, Quest):
            for cluster_key in self.game.available_clusters:
                cluster = self.game.clusters[cluster_key]
                for quest in cluster.quests:
                    if quest == unit:
                        self.tree.expanded = [cluster.key]
        self.tree.reload_sentences()
        for i, item in enumerate(self.tree.items):
            if item.obj == unit:
                self.tree.index_selected = i
                break


    def process_search(self, key):
        if key == 27:
            self.search_mode = False
            self.tree.search_text = ""
            self.tree.expanded = [v for v in self.backup_expanded]
            self.tree.index_selected = self.backup_index_selected
        elif key == ord("\n"):
            self.finish_search()
    
        elif key == curses.KEY_UP:
            self.tree.move_up()
        elif key == curses.KEY_DOWN:
            self.tree.move_down()
        elif key == 127 or key == 263 or key == 330:
            self.tree.search_text = self.tree.search_text[:-1]
        elif key >= 32 and key < 127:
            self.tree.search_text += chr(key).lower()
