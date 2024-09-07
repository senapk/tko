from typing import List, Any, Dict, Tuple, Union, Set

from ..settings.app_settings import AppSettings
from ..settings.rep_settings import RepData

from ..util.sentence import Sentence, Token
from ..util.to_asc import SearchAsc, uni_to_asc
from .flags import Flags
from ..game.game import Game
from ..game.cluster import Cluster
from ..game.quest import Quest
from ..game.task import Task
from .border import Border
from .colors import Colors
from ..util.symbols import symbols
from ..settings.settings import Settings

import os

class Entry:
    def __init__(self, obj: Union[Task, Quest, Cluster], sentence: Sentence):
        self.obj = obj
        self.sentence = sentence

    def get(self):
        return self.sentence

class TaskTree:

    def __init__(self, settings: Settings, game: Game, rep: RepData):
        self.settings = settings
        self.app = settings.app
        self.game = game
        self.rep = rep
        self.style = Border(settings.app)
        self.colors = settings.colors
        self.items: List[Entry] = []
        self.index_selected = 0
        self.index_begin = 0
        self.max_title = 0
        self.search_text = ""
        self.in_focus = True
        self.load_from_rep()
        self.update_tree(admin_mode=Flags.admin.is_true(), first_loop=True)
        self.reload_sentences()

    def set_focus(self, focus: bool):
        self.in_focus = focus

    def load_from_rep(self):
        self.new_items: List[str] = [v for v in self.rep.get_new_items()]
        self.expanded: List[str] = [v for v in self.rep.get_expanded()]
        self.index_selected = self.rep.get_index()

        tasks = self.rep.get_tasks()
        for key, serial in tasks.items():
            if key in self.game.tasks:
                self.game.tasks[key].load_from_db(serial)

    def save_on_rep(self):
        self.rep.set_expanded(self.expanded)
        self.rep.set_new_items([x for x in set(self.new_items)])
        self.rep.set_index(self.index_selected)
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
        min_value = 20
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

    def str_task(self, focus_color: str, t: Task, lig_cluster: str, lig_quest: str, quest_reachable: bool, min_value=1) -> Sentence:
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

        output = Sentence()
        output.add(" ").addf(color_aval, lig_cluster)
        output.add(" ")
        output.addf(color_aval, lig_quest)
        output.add(down_symbol)
        output.add(" ")
        output.add(t.get_grade_symbol(min_value))

        if in_focus:
            output.add(self.style.roundL(focus_color))
        else:
            output.add(" ")

        color = ""
        if in_focus:
            color = "k" + focus_color

        done = color + "g"
        todo = color
        perc = t.test_progress
        output.add(self.style.build_bar(t.title, perc / 100, len(t.title), done, todo, round=False))
        # output.addf(color, t.title)

        if in_focus:
            output.add(self.style.roundR(focus_color))
        else:
            output.add(" ")


        if Flags.reward.is_true():
            xp = ""
            for s, v in t.skills.items():
                xp += f" +{s}:{v}"
            output.addf(self.colors.task_skills, xp)
            
        return output

    def str_quest(self, has_kids: bool, focus_color: str, q: Quest, lig: str) -> Sentence:
        con = "━─"
        if q.key in self.expanded and has_kids:
            con = "─┯"

        color_reachable = "" if q.is_reachable() else "r"
        output: Sentence = Sentence().addf(color_reachable, " " + lig + con)

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

        if Flags.percent.is_true():
            output.add(" ").add(q.get_resume_by_percent())
        else:
            output.add(" ").add(q.get_resume_by_tasks())

        if Flags.minimum.is_true():
            output.add(" ").add(q.get_requirement())

        if Flags.reward.is_true():
            xp = ""
            for s, v in q.skills.items():
                xp += f" +{s}:{v}"
            output.addf(self.colors.task_skills, " " + xp)

        if q.key in self.new_items:
            output.addf(self.colors.task_new, " [new]")

        return output


    def str_cluster(self, has_kids: bool, focus_color: str, cluster: Cluster) -> Sentence:
        output: Sentence = Sentence()
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


        if Flags.percent.is_true():
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

    def get_focus_color(self, item: Union[Quest, Cluster], index: int) -> str:
        if index != self.index_selected or not self.in_focus:
            return ""
        if not item.is_reachable() and not Flags.admin.is_true():
            return "R"
        return self.colors.focused_item

    def filter_by_search(self) -> Set[str]:
        matches: Set[str] = set()
        search = SearchAsc(self.search_text)
        for cluster in self.game.clusters.values():
            if search.inside(cluster.title):
                matches.add(cluster.key)
            for quest in cluster.quests:
                if search.inside(quest.title):
                    matches.add(cluster.key)
                    matches.add(quest.key)
                for task in quest.get_tasks():
                    if search.inside(task.title):
                        matches.add(cluster.key)
                        matches.add(quest.key)
                        matches.add(task.key)
        return matches

    def try_add(self, filtered, matcher, item, sentence):
        if self.search_text == "":
            self.items.append(Entry(item, sentence))
            return True
        if item.key in filtered:
            pos = matcher.find(sentence.get_text())
            found = pos != -1
            if found:
                for i in range(pos, pos + len(self.search_text)):
                    sentence.data[i].fmt = "Y"
            self.items.append(Entry(item, sentence))
            return True
        return False

    def reload_sentences(self):
        self.update_max_title()
        index = 0
        self.items = []
        available_quests = self.game.available_quests
        available_clusters = self.game.available_clusters

        filtered = self.filter_by_search()
        matcher = SearchAsc(self.search_text)

        clusters = [self.game.clusters[key] for key in available_clusters if key in filtered]
        for cluster in clusters:
            quests = [q for q in cluster.quests if q.key in available_quests if q.key in filtered]
            focus_color = self.get_focus_color(cluster, index)
            sentence = self.str_cluster(len(quests) > 0, focus_color, cluster)

            if self.try_add(filtered, matcher, cluster, sentence):
                index += 1

            if cluster.key not in self.expanded:  # adicionou o cluster, mas não adicione as quests
                continue

            for q in quests:
                tasks =[t for t in q.get_tasks() if t.key in filtered]
                lig = "├" if q != quests[-1] else "╰"
                focus_color = self.get_focus_color(q, index)
                sentence = self.str_quest(len(tasks) > 0, focus_color, q, lig)

                # self.items.append(Entry(q, sentence))
                if self.try_add(filtered, matcher, q, sentence):
                    index += 1
                if q.key in self.expanded:
                    for t in tasks:
                        ligc = "│" if q != quests[-1] else " "
                        ligq = "├ " if t != tasks[-1] else "╰ "
                        min_value = 7 if q.tmin is None else q.tmin
                        focus_color = self.get_focus_color(q, index)
                        sentence = self.str_task(focus_color, t, ligc, ligq, q.is_reachable(), min_value)
                        if self.try_add(filtered, matcher, t, sentence):
                            index += 1

        if self.index_selected >= len(self.items):
            self.index_selected = len(self.items) - 1


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


    def mass_mark(self):
        obj = self.items[self.index_selected].obj
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
                        value = 10 if t.grade < 10 else 0
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
                        value = 10 if t.grade < 10 else 0
                        t.set_grade(value)
        else:
            obj.set_grade(10 if obj.grade < 10 else 0)

    def set_grade(self, grade: int):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            obj.set_grade(grade)

    def inc_grade(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            grade = obj.grade + 1
            if grade == 11:
                grade = 10
            obj.set_grade(grade)
        else:
            self.unfold(obj)

    
    def dec_grade(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            grade = obj.grade - 1
            if grade == -1:
                grade = 0
            obj.set_grade(grade)
        else:
            self.fold(obj)

    def arrow_right(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Cluster):
            if not self.unfold(obj):
                self.index_selected += 1
        elif isinstance(obj, Quest):
            if not self.unfold(obj):
                while True:
                    self.index_selected += 1
                    obj = self.items[self.index_selected].obj
                    if isinstance(obj, Cluster) or isinstance(obj, Quest):
                        break
                    if self.index_selected == len(self.items) - 1:
                        break
        elif isinstance(obj, Task):
            while True:
                obj = self.items[self.index_selected].obj
                if isinstance(obj, Quest) or isinstance(obj, Cluster):
                    break
                if self.index_selected == len(self.items) - 1:
                    break
                self.index_selected += 1

    def arrow_left(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Quest):
            if not self.fold(obj):
                while True:
                    if self.index_selected == 0:
                        break
                    self.index_selected -= 1
                    obj = self.items[self.index_selected].obj
                    if isinstance(obj, Cluster) or isinstance(obj, Quest) and obj.key in self.expanded:
                        break
                    if self.index_selected == 0:
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
                    if self.index_selected == 0:
                        break
                    self.index_selected -= 1
                    obj = self.items[self.index_selected].obj
                    if isinstance(obj, Cluster) or isinstance(obj, Quest):
                        break
                    if self.index_selected == 0:
                        break
        elif isinstance(obj, Task):
            while True:
                obj = self.items[self.index_selected].obj
                if isinstance(obj, Quest):
                    break
                self.index_selected -= 1

    def unfold(self, obj: Union[Task, Quest, Cluster]) -> bool:
        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
                return True
        return False

    def fold(self, obj: Union[Task, Quest, Cluster]) -> bool:
        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.key in self.expanded:
                self.expanded.remove(obj.key)
                return True
        return False

    def toggle(self, obj: Union[Quest, Cluster]):
            if not self.fold(obj):
                self.unfold(obj)

    def get_senteces(self, dy):
        if len(self.items) < dy:
            self.index_begin = 0
        else:
            if self.index_selected < self.index_begin:  # subiu na tela
                self.index_begin = self.index_selected
            elif self.index_selected >= dy + self.index_begin:  # desceu na tela
                self.index_begin = self.index_selected - dy + 1

        sentences: List[Sentence] = []
        for i in range(self.index_begin, len(self.items)):
            sentences.append(self.items[i].sentence)
        return sentences

    def get_selected(self):
        return self.items[self.index_selected].obj

    def move_up(self):
        self.index_selected = max(0, self.index_selected - 1)

    def move_down(self):
        self.index_selected = min(len(self.items) - 1, self.index_selected + 1)
