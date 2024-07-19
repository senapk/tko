from typing import List, Any, Dict

from ..settings.geral_settings import GeralSettings
from ..settings.rep_settings import RepSettings

from .floating_manager import FloatingManager
from .floating import Floating

from ..util.ftext import Sentence
from .flags import Flags
from ..game.game import Game
from ..game.cluster import Cluster
from ..game.quest import Quest
from ..game.task import Task
from ..game.xp import XP
from .style import Style

import os

class Entry:
    def __init__(self, obj: Any, sentence: Sentence):
        self.obj = obj
        self.sentence = sentence

    def get(self):
        return self.sentence


class TaskTree:

    def __init__(self, local: GeralSettings, game: Game, rep: RepSettings, rep_alias: str):
        self.local = local
        self.game = game
        self.rep = rep
        self.rep_alias = rep_alias

        self.available_quests: List[Quest] = []
        self.available_clusters: List[Cluster] = []

        self.items: List[Entry] = []
        # self.new_items: List[str] = []
        # self.expanded: List[str] = []

        self.index_selected = 0
        self.index_begin = 0

        self.max_title = 0

        self.load_from_rep()

        self.update_available()
        self.reload_sentences()

    def load_from_rep(self):
        self.new_items: List[str] = self.rep.get_new_items()
        self.expanded: List[str] = self.rep.get_expanded()

        tasks = self.rep.get_tasks()
        for key, grade in tasks.items():
            if key in self.game.tasks:
                self.game.tasks[key].set_grade(int(grade))

    def save_on_rep(self):
        self.rep.set_expanded(self.expanded)
        self.rep.set_new_items(self.new_items)
        tasks = {}
        for t in self.game.tasks.values():
            if t.grade != 0:
                tasks[t.key] = str(t.grade)
        self.rep.set_tasks(tasks)

    def update_available(self):
        old_quests = [q for q in self.available_quests]
        old_clusters = [c for c in self.available_clusters]
        if Flags.admin.is_true():
            self.available_quests = list(self.game.quests.values())
            self.available_clusters = [c for c in self.game.clusters]
        else:
            self.available_quests = self.game.get_reachable_quests()
            self.available_clusters = []
            for c in self.game.clusters:
                if any([q in self.available_quests for q in c.quests]):
                    self.available_clusters.append(c)

        removed_clusters = [c for c in old_clusters if c not in self.available_clusters]
        for c in removed_clusters:
            if c.key in self.expanded:
                self.expanded.remove(c.key)
        removed_quests = [q for q in old_quests if q not in self.available_quests]
        for q in removed_quests:
            if q.key in self.expanded:
                self.expanded.remove(q.key)

        added_clusters = [c for c in self.available_clusters if c not in old_clusters]
        added_quests = [q for q in self.available_quests if q not in old_quests]

        for c in added_clusters:
            if c.key not in self.new_items:
                self.new_items.append(c.key)
        for q in added_quests:
            if q.key not in self.new_items:
                self.new_items.append(q.key)

        self.new_items = [item for item in self.new_items if item not in self.expanded]


    def update_max_title(self):
        items = []
        for c in self.available_clusters:
            items.append(len(c.title))
            if c.key in self.expanded:
                for q in c.quests:
                    items.append(len(q.title) + 2)
        self.max_title = max(items)

    def str_task(self, in_focus: bool, t: Task, lig_cluster: str, lig_quest: str, min_value=1) -> Sentence:
        output = Sentence()
        output.add(" " + lig_cluster + " " + lig_quest)
        output.add(t.get_grade_symbol(min_value))
        output.add(" ")

        color = ""
        if Flags.opt.is_true() and t.opt:
            color = Style.opt_task + color
        if in_focus:
            color = Flags.focus.get_value() + color
        output.addf(color, t.title)

        if Flags.xp.is_true():
            xp = ""
            for s, v in t.skills.items():
                xp += f" +{s}:{v}"
            output.addf(Style.skills, xp)
            
        if Flags.path.is_true():
            rootdir = self.local.get_rootdir()
            if rootdir != "":
                path = os.path.join(self.local.get_rootdir(), self.rep_alias, t.key, "Readme.md")
                # if Flags.relative.is_true():
                #     path = os.path.relpath(path)
                if os.path.isfile(path):
                    output.add(" ").addf("y", f"[{path}]")

        return output

    def str_quest(self, in_focus: bool, q: Quest, lig: str) -> Sentence:
        con = "━─" if q.key not in self.expanded else "─┯"
        output: Sentence = Sentence().add(" " + lig + con + " ")

        color = ""
        if Flags.opt.is_true() and q.opt:
            color = Style.opt_quest + color
        if in_focus:
            color = Flags.focus.get_value() + color

        title = q.title
        if Flags.dots.is_true():
            title = title.ljust(self.max_title - 2, ".")
        # if Flags.quest_prog.is_true():
        done = color + Flags.prog_done.get_value()
        todo = color + Flags.prog_todo.get_value()
        output.add(Sentence.build_bar(title, q.get_percent() / 100, len(title), done, todo))
        # else:
        #     output.addf(color, title)

        if Flags.count.is_true():
            if Flags.percent.is_true():
                output.add(" ").add(q.get_resume_by_percent())
            else:
                output.add(" ").add(q.get_resume_by_tasks())

        if Flags.minimum.is_true():
            output.add(" ").add(q.get_requirement())

        if Flags.xp.is_true():
            xp = ""
            for s, v in q.skills.items():
                xp += f" +{s}:{v}"
            output.addf(Style.skills, " " + xp)

        if q.key in self.new_items:
            output.addf(Style.new, " [new]")

        return output

    def str_cluster(self, in_focus: bool, cluster: Cluster) -> Sentence:
        output: Sentence = Sentence()
        opening = "━─"
        if cluster.key in self.expanded:
            opening = "─┯"
        output.add(opening + " ")
        color = Style.cluster_title
        if in_focus:
            color += Flags.focus.get_value() + color
        title = cluster.title
        if Flags.dots.is_true():
            title = cluster.title.ljust(self.max_title, ".")

        # if Flags.group_prog.is_true():
        done = color + Flags.prog_done.get_value()
        todo = color + Flags.prog_todo.get_value()
        output.add(Sentence.build_bar(title, cluster.get_percent() / 100, len(title), done, todo))
        # else:
        #     output.addf(color, title)

        if Flags.count.is_true():
            if Flags.percent.is_true():
                output.add(" ").add(cluster.get_resume_by_percent())
            else:
                output.add(" ").add(cluster.get_resume_by_quests())
        if cluster.key in self.new_items:
            output.addf(Style.new, " [new]")

        return output

    def get_available_quests_from_cluster(self, cluster: Cluster) -> List[Quest]:
        return [q for q in cluster.quests if q in self.available_quests]

    def reload_sentences(self):
        self.update_max_title()
        index = 0
        self.items = []
        for cluster in self.available_clusters:
            quests = self.get_available_quests_from_cluster(cluster)
            sentence = self.str_cluster(self.index_selected == index, cluster)
            self.items.append(Entry(cluster, sentence))
            index += 1

            if cluster.key not in self.expanded:  # va para proximo cluster
                continue

            for q in quests:
                lig = "├" if q != quests[-1] else "╰"
                sentence = self.str_quest(self.index_selected == index, q, lig)
                self.items.append(Entry(q, sentence))
                index += 1
                if q.key in self.expanded:
                    for t in q.get_tasks():
                        ligc = "│" if q != quests[-1] else " "
                        ligq = "├ " if t != q.get_tasks()[-1] else "╰ "
                        min_value = 7 if q.tmin is None else q.tmin
                        sentence = self.str_task(self.index_selected == index, t, ligc, ligq, min_value)
                        self.items.append(Entry(t, sentence))
                        index += 1

        if self.index_selected >= len(self.items):
            self.index_selected = len(self.items) - 1


    def process_collapse(self):
        quest_keys = [q.key for q in self.available_quests]
        if any([q in self.expanded for q in quest_keys]):
            self.expanded = [key for key in self.expanded if key not in quest_keys]
        else:
            self.expanded = []

    def process_expand(self):
        # if any cluster outside expanded
        expand_clusters = False
        for c in self.available_clusters:
            if c.key not in self.expanded:
                expand_clusters = True
        if expand_clusters:
            for c in self.available_clusters:
                if c.key not in self.expanded:
                    self.expanded.append(c.key)
        else:
            for q in self.available_quests:
                if q.key not in self.expanded:
                    self.expanded.append(q.key)


    def mass_mark(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Cluster):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
                return
            full_open = True
            for q in self.get_available_quests_from_cluster(obj):
                if q.key not in self.expanded:
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

    def arrow_right(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Cluster):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
            else:
                self.index_selected += 1
        elif isinstance(obj, Quest):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
            else:
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
            if obj.key in self.expanded:
                self.expanded.remove(obj.key)
            else:
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

    def expand(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)

    def toggle(self):
        obj = self.items[self.index_selected].obj
        if isinstance(obj, Task):
            if obj.grade < 10:
                obj.set_grade(10)
            else:
                obj.set_grade(0)
        elif isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.key in self.expanded:
                self.expanded.remove(obj.key)
            else:
                self.expanded.append(obj.key)

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
