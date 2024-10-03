from typing import List, Any, Dict, Tuple, Union, Set

from tko.settings.app_settings import AppSettings
from tko.settings.rep_settings import RepData

from tko.util.text import Text, Token
from tko.util.to_asc import SearchAsc, uni_to_asc
from tko.play.flags import Flags
from tko.game.game import Game
from tko.game.cluster import Cluster
from tko.game.quest import Quest
from tko.game.task import Task
from tko.play.border import Border
from tko.play.colors import Colors
from tko.util.symbols import symbols
from tko.settings.settings import Settings
from tko.play.floating_manager import FloatingManager
from tko.play.floating import Floating
from tko.play.grade_message import GradeMessage
from tko.game.tree_item import TreeItem

import os

class TaskTree:

    def __init__(self, settings: Settings, game: Game, rep: RepData, fman: FloatingManager):
        self.settings = settings
        self.app = settings.app
        self.game = game
        self.rep = rep
        self.fman = fman
        self.style = Border(settings.app)
        self.colors = settings.colors
        self.items: List[TreeItem] = []
        self.all_items: Dict[str, TreeItem] = {}
        self.selected_item: str = ""
        self.index_begin = 0
        self.max_title = 0
        self.search_text = ""
        self.load_all_items()
        self.load_from_rep()
        self.update_tree(admin_mode=Flags.admin, first_loop=True)
        self.reload_sentences()

    def load_all_items(self):
        for c in self.game.clusters.values():
            self.all_items[c.key] = c
            for q in c.quests:
                self.all_items[q.key] = q
                for t in q.get_tasks():
                    self.all_items[t.key] = t

    def load_from_rep(self):
        self.new_items: List[str] = [v for v in self.rep.get_new_items()]
        self.expanded: List[str] = [v for v in self.rep.get_expanded()]
        self.selected_item = self.rep.get_selected()

        tasks = self.rep.get_tasks()
        for key, serial in tasks.items():
            if key in self.game.tasks:
                self.game.tasks[key].load_from_db(serial)

    def save_on_rep(self):
        self.rep.set_expanded(self.expanded)
        self.rep.set_new_items([x for x in set(self.new_items)])
        self.rep.set_selected(self.selected_item)
        tasks = {}
        for t in self.game.tasks.values():
            if not t.is_db_empty():
                tasks[t.key] = t.save_to_db()
        self.rep.set_tasks(tasks)


    def update_tree(self, admin_mode: bool, first_loop: bool = False):
        if not admin_mode:
            old_reachable = self.game.available_clusters + self.game.available_quests

        self.game.update_reachable_and_available(admin_mode)
            
        if not admin_mode:
            available_keys = self.game.available_quests + self.game.available_clusters
            for key in self.expanded:
                if key not in available_keys:
                    self.expanded.remove(key)
            if not first_loop:
                for key in available_keys:
                    if key not in old_reachable and key not in self.new_items:
                        self.new_items.append(key)

        # remove expanded items from new
        self.new_items = [item for item in self.new_items if item not in self.expanded]

    def update_max_title(self):
        min_value = 50
        items = []
        for c in self.game.clusters.values():
            if c.key in self.game.available_clusters:
                items.append(len(c.title))
                if c.key in self.expanded:
                    for q in [q for q in c.quests if q.key in self.game.available_quests]:
                        items.append(len(q.title) + 2)
                        if q.key in self.expanded:
                            for t in q.get_tasks():
                                items.append(len(t.title) + 6)
        self.max_title = max(items)
        if self.max_title < min_value:
            self.max_title = min_value

    def str_task(self, focus_color: str, t: Task, lig_cluster: str, lig_quest: str, quest_reachable: bool, min_value=1) -> Text:
        # downloadable_in_focus = False
        rootdir = self.app._rootdir
        down_symbol = Token(" ")
        in_focus = focus_color != ""
        down_symbol = symbols.cant_download
        rep_dir = os.path.join(self.app.get_rootdir(), self.rep.alias)
        if t.is_downloadable() and rootdir != "":
            if t.is_downloaded_for_lang(rep_dir, self.rep.get_lang()):
                down_symbol = symbols.downloaded
                # if in_focus:
                #     downloadable_in_focus = True
            else:
                down_symbol = symbols.to_download

        color_aval = "" if quest_reachable else "r"

        output = Text()
        output.add(" ").addf(color_aval, lig_cluster)
        output.add(" ")
        output.addf(color_aval, lig_quest)
        output.add(down_symbol).add(" ")
        output.add(t.get_prog_symbol()).add(" ")
        output.add(GradeMessage().grade_to_emojis(t.self_grade))

        if in_focus:
            output.add(self.style.roundL(focus_color))
        else:
            output.add(" ")

        color = ""
        if in_focus:
            color = "k" + focus_color

        done = color + "g"
        todo = color
        perc = t.progress
        output.add(self.style.build_bar(t.title, perc / 100, len(t.title), done, todo, round=False))
        # output.addf(color, t.title)

        if in_focus:
            output.add(self.style.roundR(focus_color))
        else:
            output.add(" ")


        if Flags.reward:
            xp = ""
            for s, v in t.skills.items():
                xp += f" +{s}:{v}"
            output.addf(self.colors.task_skills, xp)
            
        return output

    def str_quest(self, has_kids: bool, focus_color: str, q: Quest, lig: str) -> Text:
        con = "━─"
        if q.key in self.expanded and has_kids:
            con = "─┯"

        color_reachable = "" if q.is_reachable() else "r"
        output: Text = Text().addf(color_reachable, " " + lig + con)

        in_focus = focus_color != ""
        if in_focus:
            output.add(self.style.roundL(focus_color))
        else:
            output.add(" ")

        color = ""
        if in_focus:
            color = "k" + focus_color

        title = q.title
        title = title.ljust(self.max_title - 2, ".")

        done = color + self.colors.task_text_done
        todo = color + self.colors.task_text_todo
        output.add(self.style.build_bar(title, q.get_percent() / 100, len(title), done, todo, round=False))

        if in_focus:
            output.add(self.style.roundR(focus_color))
        else:
            output.add(" ")

        if Flags.percent:
            output.add(" ").add(q.get_resume_by_percent())
        else:
            output.add(" ").add(q.get_resume_by_tasks())

        if Flags.minimum:
            output.add(" ").add(q.get_requirement())

        if Flags.reward:
            xp = ""
            for s, v in q.skills.items():
                xp += f" +{s}:{v}"
            output.addf(self.colors.task_skills, xp)

        if q.key in self.new_items:
            output.addf(self.colors.task_new, " [new]")

        return output


    def str_cluster(self, has_kids: bool, focus_color: str, cluster: Cluster) -> Text:
        output: Text = Text()
        opening = "━─"
        if cluster.key in self.expanded and has_kids:
            opening = "─┯"
        color_reachable = "" if cluster.is_reachable() else "r"
        output.addf(color_reachable, opening)

        color = ""
        if focus_color != "":
            color = "k" + focus_color
        title = cluster.title

        title = cluster.title.ljust(self.max_title, ".")
        if focus_color != "":
            output.add(self.style.roundL(focus_color))
        else:
            output.add(" ")

        done = color + self.colors.task_text_done
        todo = color + self.colors.task_text_todo

        output.add(self.style.build_bar(title, cluster.get_percent() / 100, len(title), done, todo, round=False))

        if focus_color != "":
            output.add(self.style.roundR(focus_color))
        else:
            output.add(" ")


        if Flags.percent:
            output.add(" ").add(cluster.get_resume_by_percent())
        else:
            output.add(" ").add(cluster.get_resume_by_quests())
        if cluster.key in self.new_items:
            output.addf(self.colors.task_new, " [new]")

        return output


    # def add_in_search(self, item: Any, sentence: Sentence) -> bool:
    #     if self.search_text == "":
    #         self.items.append(Entry(item, sentence))
    #         return True
        
    #     matcher = SearchAsc(self.search_text)
    #     pos = matcher.find(sentence.get_text())
    #     found = pos != -1
    #     if found:
    #         for i in range(pos, pos + len(self.search_text)):
    #             sentence.data[i].fmt = "Y"

    #     if isinstance(item, Task):
    #         if found:
    #             self.items.append(Entry(item, sentence))
    #             return True
    #     elif isinstance(item, Quest):
    #         if found:
    #             self.items.append(Entry(item, sentence))
    #             return True
    #         for t in item.get_tasks():
    #             if matcher.inside(t.title):
    #                 self.items.append(Entry(item, sentence))
    #                 return True
    #     elif isinstance(item, Cluster):
    #         cluster: Cluster = item
    #         if matcher.inside(cluster.title):
    #             self.items.append(Entry(cluster, sentence))
    #             return True
    #         for q in cluster.quests:
    #             if matcher.inside(q.title):
    #                 self.items.append(Entry(item, sentence))
    #                 return True
    #             for t in q.get_tasks():
    #                 if matcher.inside(t.title):
    #                     self.items.append(Entry(item, sentence))
    #                     return True
    #     return False

    def get_focus_color(self, item: Union[Quest, Cluster]) -> str:
        if not item.is_reachable() and Flags.admin:
            return "R"
        return self.colors.focused_item

    def filter_by_search(self) -> Tuple[Set[str], str | None]:
        matches: Set[str] = set()
        search = SearchAsc(self.search_text)
        first: None | str = None
        for cluster in self.game.clusters.values():
            if search.inside(cluster.title):
                matches.add(cluster.key)
                first = first or cluster.key
            for quest in cluster.quests:
                if search.inside(quest.title):
                    first = first or quest.key
                    matches.add(cluster.key)
                    matches.add(quest.key)
                for task in quest.get_tasks():
                    if search.inside(task.title):
                        first = first or task.key
                        matches.add(cluster.key)
                        matches.add(quest.key)
                        matches.add(task.key)
        return (matches, first)

    def try_add(self, filtered: set[str], matcher: SearchAsc, item: TreeItem):
        if self.search_text == "":
            self.items.append(item)
            return True
        if item.key in filtered:
            pos = matcher.find(item.sentence.get_text())
            found = pos != -1
            if found:
                for i in range(pos, pos + len(self.search_text)):
                    item.sentence.data[i].fmt = "Y"
            self.items.append(item)
            return True
        return False

    def reload_sentences(self):
        self.update_max_title()
        self.items = []
        available_quests = self.game.available_quests
        available_clusters = self.game.available_clusters

        filtered, _ = self.filter_by_search()
        matcher = SearchAsc(self.search_text)

        clusters = [self.game.clusters[key] for key in available_clusters if key in filtered]
        for cluster in clusters:
            quests = [q for q in cluster.quests if q.key in available_quests if q.key in filtered]
            focus_color = self.get_focus_color(cluster) if self.selected_item == cluster.get_key() else ""
            cluster.sentence = self.str_cluster(len(quests) > 0, focus_color, cluster)

            self.try_add(filtered, matcher, cluster)

            if cluster.key not in self.expanded:  # adicionou o cluster, mas não adicione as quests
                continue

            for q in quests:
                tasks =[t for t in q.get_tasks() if t.key in filtered]
                lig = "├" if q != quests[-1] else "╰"
                focus_color = self.get_focus_color(q) if self.selected_item == q.get_key() else ""
                q.sentence = self.str_quest(len(tasks) > 0, focus_color, q, lig)

                # self.items.append(Entry(q, sentence))
                self.try_add(filtered, matcher, q)
                if q.key in self.expanded:
                    for t in tasks:
                        ligc = "│" if q != quests[-1] else " "
                        ligq = "├ " if t != tasks[-1] else "╰ "
                        min_value = 7 if q.tmin is None else q.tmin
                        focus_color = self.get_focus_color(q) if self.selected_item == t.get_key() else ""
                        t.sentence = self.str_task(focus_color, t, ligc, ligq, q.is_reachable(), min_value)
                        self.try_add(filtered, matcher, t)


    def process_collapse(self):
        if any([q in self.expanded for q in self.game.available_quests]):
            self.expanded = [key for key in self.expanded if key not in self.game.available_quests]
        else:
            self.expanded = []

    def process_expand(self):
        # if any cluster outside expanded
        expand_clusters = False
        for ckey in self.game.available_clusters:
            if ckey not in self.expanded:
                expand_clusters = True
        if expand_clusters:
            for ckey in self.game.available_clusters:
                if ckey not in self.expanded:
                    self.expanded.append(ckey)
        else:
            for qkey in self.game.available_quests:
                if qkey not in self.expanded:
                    self.expanded.append(qkey)

    def get_selected_index(self) -> int:
        for i, item in enumerate(self.items):
            if item.key == self.selected_item:
                return i
        return 0

    def get_selected(self) -> TreeItem:
        index = self.get_selected_index()
        return self.items[index]

    def mass_mark(self):
        obj = self.get_selected()
        if isinstance(obj, Cluster):
            cluster: Cluster = obj
            if cluster.key not in self.expanded:
                self.expanded.append(cluster.key)
                return
            full_open = True
            for q in cluster.quests:
                if q.key in self.game.available_quests and q.key not in self.expanded:
                    self.expanded.append(q.key)
                    full_open = False
            if not full_open:
                return

            value = None
            for q in obj.quests:
                for t in q.get_tasks():
                    if value is not None:
                        t.set_grade(value)
                    else:
                        value = 10 if t.self_grade < 10 else 0
                        t.set_grade(value)
        elif isinstance(obj, Quest):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
            else:
                value = None
                for t in obj.get_tasks():
                    if value is not None:
                        t.set_grade(value)
                    else:
                        value = 10 if t.self_grade < 10 else 0
                        t.set_grade(value)
        elif isinstance(obj, Task):
            obj.set_grade(10 if obj.self_grade < 10 else 0)

    def set_grade(self, grade: int):

        obj = self.get_selected()
        if isinstance(obj, Task):
            obj.set_grade(grade)
            self.fman.add_input(
                Floating("v").warning().set_header(" Auto avaliação ").set_text_ljust().set_content(GradeMessage().format(grade).split("\n"))
            )

    def set_progress(self, prog: int):

        obj = self.get_selected()
        if isinstance(obj, Task):
            obj.progress = prog

    def inc_progress(self):
        obj = self.get_selected()
        if isinstance(obj, Task):
            progress = obj.progress + 10
            if progress > 100:
                progress = 100
            self.set_progress(progress)

    def dec_progress(self):
        obj = self.get_selected()
        if isinstance(obj, Task):
            progress = obj.progress - 10
            if progress < 0:
                progress = 0
            self.set_progress(progress)

    def inc_self_grade(self):
        obj = self.get_selected()
        if isinstance(obj, Task):
            grade = obj.self_grade + 1
            if grade >= 10:
                grade = 10
            self.set_grade(grade)
        else:
            self.unfold(obj)

    
    def dec_self_grade(self):
        obj = obj = self.get_selected()
        if isinstance(obj, Task):
            grade = obj.self_grade - 1
            if grade == -1:
                grade = 0
            self.set_grade(grade)
        else:
            self.fold(obj)

    def set_selected_by_index(self, index: int):
        if index < 0:
            index = 0
        if index >= len(self.items):
            index = len(self.items) - 1
        self.selected_item = self.items[index].key

    def arrow_right(self):
        index = self.get_selected_index()
        obj = self.items[index]
        if isinstance(obj, Cluster):
            if not self.unfold(obj):
                self.set_selected_by_index(index + 1)
        elif isinstance(obj, Quest):
            if not self.unfold(obj):
                while True:
                    index += 1
                    if index >= len(self.items):
                        break
                    obj = self.items[index]
                    if isinstance(obj, Cluster) or isinstance(obj, Quest):
                        break
                self.set_selected_by_index(index)
        elif isinstance(obj, Task):
            while True:
                obj = self.items[index]
                if isinstance(obj, Quest) or isinstance(obj, Cluster):
                    break
                if index == len(self.items) - 1:
                    break
                index += 1
            self.set_selected_by_index(index)

    def arrow_left(self):
        index = self.get_selected_index()
        obj = self.items[index]
        if isinstance(obj, Quest):
            if not self.fold(obj):
                while True:
                    if self.selected_item == 0:
                        break
                    index -= 1
                    obj = self.items[index]
                    if isinstance(obj, Cluster) or isinstance(obj, Quest) and obj.key in self.expanded:
                        break
                    if self.selected_item == 0:
                        break
        elif isinstance(obj, Cluster):
            if obj.key in self.expanded:
                self.expanded.remove(obj.key)
                for q in obj.quests:
                    try:
                        self.expanded.remove(q.key)
                    except ValueError:
                        pass
            else:
                while True:
                    if self.selected_item == 0:
                        break
                    index -= 1
                    obj = self.items[index]
                    if isinstance(obj, Cluster) or isinstance(obj, Quest):
                        break
                    if self.selected_item == 0:
                        break
        elif isinstance(obj, Task):
            while True:
                obj = self.items[index]
                if isinstance(obj, Quest):
                    break
                index -= 1
        self.set_selected_by_index(index)

    def unfold(self, obj: TreeItem) -> bool:
        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
                return True
        return False

    def fold(self, obj: TreeItem) -> bool:
        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.key in self.expanded:
                self.expanded.remove(obj.key)
                return True
        return False

    def toggle(self, obj: Union[Quest, Cluster]):
            if not self.fold(obj):
                self.unfold(obj)

    def get_senteces(self, dy):
        index = self.get_selected_index()
        if len(self.items) < dy:
            self.index_begin = 0
        else:
            if index < self.index_begin:  # subiu na tela
                self.index_begin = index
            elif index >= dy + self.index_begin:  # desceu na tela
                self.index_begin = index - dy + 1

        sentences: List[Text] = []
        for i in range(self.index_begin, len(self.items)):
            sentences.append(self.items[i].sentence)
        return sentences

    def move_up(self):
        index = self.get_selected_index()
        self.set_selected_by_index(index - 1)

    def move_down(self):
        index = self.get_selected_index()
        self.set_selected_by_index(min(len(self.items) - 1, index + 1))
