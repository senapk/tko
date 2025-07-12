from tko.settings.repository import Repository
from tko.util.text import Text
from tko.util.to_asc import SearchAsc
from tko.play.flags import Flags
from tko.game.cluster import Cluster
from tko.game.quest import Quest
from tko.game.task import Task
from tko.play.border import Border
from tko.down.drafts import Drafts
from tko.settings.settings import Settings
from tko.play.floating_manager import FloatingManager
from tko.util.symbols import symbols
from tko.game.tree_item import TreeItem

class TaskAction:
    BAIXAR   = "Baixar  "
    EXECUTAR = "Escolher"
    VISITAR  = "Visitar "
    EXPANDIR = "Expandir"
    CONTRAIR = "Contrair"
    BLOQUEIO = "Travado"

class TaskTree:

    def __init__(self, settings: Settings, rep: Repository, fman: FloatingManager):
        self.settings = settings
        self.app = settings.app
        self.game = rep.game
        self.rep = rep
        self.fman = fman
        self.style = Border(settings.app)
        self.colors = settings.colors
        self.items: list[TreeItem] = []
        self.all_items: dict[str, TreeItem] = {}
        self.selected_item: str = ""
        self.index_begin: int = 0
        self.max_title: int = 0
        self.search_text: str = ""
        self.expanded: list[str] = []
        self.load_all_items()
        self.load_from_rep()
        self.update_tree(admin_mode = Flags.admin.is_true())
        self.reload_sentences()

    def load_all_items(self):
        for c in self.game.clusters.values():
            self.all_items[c.key] = c
            for q in c.get_quests():
                self.all_items[q.key] = q
                for t in q.get_tasks():
                    self.all_items[t.key] = t

    def load_from_rep(self):
        # self.new_items: list[str] = [v for v in self.rep.get_new_items()]
        self.expanded: list[str] = [v for v in self.rep.get_expanded()]
        self.selected_item = self.rep.get_selected()

        # tasks = self.rep.get_tasks()
        # for key, serial in tasks.items():
        #     if key in self.game.tasks:
        #         self.game.tasks[key].load_from_db(serial)

    def save_on_rep(self):
        self.rep.set_expanded(self.expanded)
        # self.rep.set_new_items([x for x in set(self.new_items)])
        self.rep.set_selected(self.selected_item)
        tasks: dict[str, str] = {}
        for t in self.game.tasks.values():
            if len(t.info.get_filled_kv()) != 0:
                tasks[t.key] = t.save_to_db()
        self.rep.set_tasks(tasks)

    def update_tree(self, admin_mode: bool):
        #if not admin_mode:
            # reachable_clusters = [c.key for c in self.game.clusters.values() if c.is_reachable()]
            # reachable_quests = [q.key for q in self.game.quests.values() if q.is_reachable()]
            # old_reachable = reachable_clusters + reachable_quests

        self.game.update_reachable_and_available()
            
        if not admin_mode:
            # reachable_clusters = [c.key for c in self.game.clusters.values() if c.is_reachable()]
            reachable_quests = [q.key for q in self.game.quests.values() if q.is_reachable()]
            reachable_keys = reachable_quests + list(self.game.clusters.keys())
            for key in self.expanded:
                if key not in reachable_keys:
                    self.expanded.remove(key)
            # if not first_loop:
            #     for key in reachable_keys:
            #         if key not in old_reachable and key not in self.new_items:
            #             self.new_items.append(key)

        # remove expanded items from new
        # self.new_items = [item for item in self.new_items if item not in self.expanded]

    def __update_max_title(self):
        min_value = 50
        items: list[int] = []
        for c in self.game.clusters.values():
            if c.key in self.game.clusters.keys():
                items.append(len(c.title))
                if c.key in self.expanded:
                    for q in c.get_quests():
                        items.append(len(q.get_full_title()) + 2)
                        if q.key in self.expanded:
                            for t in q.get_tasks():
                                items.append(len(t.title) + 6)

        self.max_title = min_value
        if len(items) > 0:
            self.max_title = max(items)
        if self.max_title < min_value:
            self.max_title = min_value

    def __str_task(self, focus_color: str, t: Task, lig_cluster: str, lig_quest: str, quest_reachable: bool) -> Text:
        # down_symbol = Text.Token(" ")
        in_focus = focus_color != ""
        down_symbol = symbols.task_to_visit
        if t.link_type == Task.Types.STATIC_FILE:
            down_symbol = symbols.task_local
        if t.link_type == Task.Types.REMOTE_FILE or t.link_type == Task.Types.IMPORT_FILE:
            down_symbol = symbols.task_to_download
            if self.is_downloaded_for_lang(t):
                down_symbol = symbols.task_downloaded
    
        color_aval = "g" if quest_reachable and t.is_reachable() else "r"
        color_lig_task = color_aval
        if self.app.get_show_hidden() == False and not Flags.admin:
            quest = self.game.quests[t.quest_key]
            if quest.prog:
                if t.key != self.game.quests[t.quest_key].get_tasks()[-1].key:
                    if t.get_percent() < 50:
                        color_lig_task = "y"
                    

        output = Text()
        output.add(" ").addf(color_aval, lig_cluster)
        output.add(" ")
        output.addf(color_lig_task, lig_quest)
        output.add(down_symbol).add(" ")
        output.add(t.get_prog_symbol()).add(" ")
        output.add(symbols.flow_list[t.info.flow]).add(" ")
        output.add(symbols.edge_list[t.info.edge])


        if in_focus:
            output.add(self.style.round_l(focus_color))
        else:
            output.add(" ")

        color = ""
        if in_focus:
            color = "k" + focus_color

        for word in t.title.split(" "):
            if word.startswith("@") or word.startswith("#") or word.startswith("!"):
                output.addf(color + "g", word + " ")
            elif word.startswith(":"):
                output.addf(color + "y", word + " ")
            elif word.startswith("*"):
                output.addf(color + "c", word + " ")
            elif word.startswith("+"):
                output.addf(color + "c", word + " ")
            else:
                output.addf(color, word + " ")

        if in_focus:
            output.add(self.style.round_r(focus_color))
        else:
            output.add(" ")

        output.ljust(self.max_title + 10, Text.Token(" "))
        if Flags.percent.is_true():
            prog = round(t.get_percent())
            output.addf("y", str(prog).rjust(3, " ") + "%")
        else:
            color_rate: list[str] = ["", "c", "g", "y", "m", "r"]
            rate = (t.info.neat + t.info.cool) / 2
            for i in range(1, 6):
                if rate >= i:
                    output.addf(color_rate[t.info.easy], symbols.star)
                else:
                    output.addf(color_rate[t.info.easy], symbols.open_star)

        # if Flags.reward:
        #     xp = ""
        #     for s, v in t.skills.items():
        #         xp += f" +{s}:{v}"
        #     output.addf(self.colors.task_skills, xp)
            
        return output

    def __str_quest(self, has_kids: bool, focus_color: str, q: Quest, lig: str) -> Text:
        con = "━─"
        if q.key in self.expanded and has_kids:
            con = "─┯"

        color_reachable = "g" if q.is_reachable() else "r"
        if self.app.get_show_hidden() == False and not Flags.admin:
            for quest in self.game.quests.values():
                if not quest.is_reachable():
                    if q.key in quest.requires:
                        color_reachable = "y"
                        break

        output: Text = Text().addf(color_reachable, " " + lig + con)

        in_focus = focus_color != ""

        if focus_color == "":
            item_key = self.selected_item
            if item_key in list(self.game.quests.keys()):
                quest = self.game.quests[item_key]
                if not quest.is_reachable():
                    if q.key in quest.requires:
                        focus_color = "y"
                # elif quest.key in q.requires:
                #     focus_color = "r"

        if in_focus:
            output.add(self.style.round_l(focus_color))
        else:
            output.add(" ")

        # color = ""
        # if in_focus:
        #     color = "k" + focus_color

        title = q.get_full_title()
        title = title.ljust(self.max_title + 3, ".")

        output.addf(focus_color, title)

        if in_focus:
            output.add(self.style.round_r(focus_color))
        else:
            output.add(" ")

        # if Flags.percent:
        output.add(" ").add(q.get_resume_by_percent())
        all_tasks_done = True
        for t in q.get_tasks():
            if not t.is_complete():
                all_tasks_done = False
                break
        if all_tasks_done:
            output.add("🌟")

        # if Flags.minimum:
        #     output.add(" ").add(q.get_requirement())

        # if Flags.reward:
        #     xp = ""
        #     for s, v in q.skills.items():
        #         xp += f" +{s}:{v}"
        #     output.addf(self.colors.task_skills, xp)

        # if q.key in self.new_items:
        #     output.addf(self.colors.task_new, " [new]")

        return output

    def __str_cluster(self, has_kids: bool, focus_color: str, cluster: Cluster) -> Text:
        output: Text = Text()
        opening = "━─"
        if cluster.key in self.expanded and has_kids:
            opening = "─┯"
        color_reachable = "g" if cluster.is_reachable() else "r"
        output.addf(color_reachable, opening)

        color = ""
        if focus_color != "":
            color = "k" + focus_color

        title = cluster.title.ljust(self.max_title + 5, ".")
        if focus_color != "":
            output.add(self.style.round_l(focus_color))
        else:
            output.add(" ")

        output.addf(color, title)

        if focus_color != "":
            output.add(self.style.round_r(focus_color))
        else:
            output.add(" ")


        # if Flags.percent:
        output.add(" ").add(cluster.get_resume_by_percent())
        # else:
        #     output.add(" ").add(cluster.get_resume_by_quests())
        # if cluster.key in self.new_items:
        #     output.addf(self.colors.task_new, " [new]")

        return output

    def __get_focus_color_cluster(self, item: Cluster) -> str:
        if not item.is_reachable():
            return "R"
        return self.colors.focused_item
    
    def __get_focus_color_quest(self, item: Quest) -> str:
        if not item.is_reachable():
                return "R"
        return self.colors.focused_item

    def filter_by_search(self) -> tuple[set[str], str | None]:
        matches: set[str] = set()
        search = SearchAsc(self.search_text)
        first: None | str = None
        for cluster in self.game.clusters.values():
            if search.inside(cluster.title):
                matches.add(cluster.key)
                first = first or cluster.key
            for quest in cluster.get_quests():
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
        return matches, first

    def __try_add(self, filtered: set[str], matcher: SearchAsc, item: TreeItem):
        if self.search_text == "":
            self.items.append(item)
            return True
        if item.key in filtered:
            pos = matcher.find(item.sentence.get_str())
            found = pos != -1
            if found:
                for i in range(pos, pos + len(self.search_text)):
                    item.sentence.data[i].fmt = "Y"
            self.items.append(item)
            return True
        return False

    def reload_sentences(self):
        self.__update_max_title()
        self.items = []

        filtered, _ = self.filter_by_search()
        matcher = SearchAsc(self.search_text)

        hide = not self.app.get_show_hidden() and not Flags.admin

        clusters = [self.game.clusters[key] for key in self.game.clusters.keys() if key in filtered]
        if hide:
            clusters = [c for c in clusters if c.is_reachable()]

        for cluster in clusters:
            quests = [q for q in cluster.get_quests() if q.key in self.game.quests.keys() if q.key in filtered]
            if hide:
                quests = [q for q in quests if q.is_reachable()]
            focus_color = self.__get_focus_color_cluster(cluster) if self.selected_item == cluster.get_key() else ""
            cluster.sentence = self.__str_cluster(len(quests) > 0, focus_color, cluster)

            self.__try_add(filtered, matcher, cluster)

            if cluster.key not in self.expanded:  # adicionou o cluster, mas não adicione as quests
                continue

            for q in quests:
                tasks =[t for t in q.get_tasks() if t.key in filtered]
                if hide:
                    tasks = [t for t in tasks if t.is_reachable()]
                lig = "├" if q != quests[-1] else "╰"
                quest_focus_color: str = self.__get_focus_color_quest(q)
                focus_color = quest_focus_color if self.selected_item == q.get_key() else ""
                q.sentence = self.__str_quest(len(tasks) > 0, focus_color, q, lig)

                # self.items.append(Entry(q, sentence))
                self.__try_add(filtered, matcher, q)
                if q.key in self.expanded:
                    for t in tasks:
                        ligc = "│" if q != quests[-1] else " "
                        ligq = "├ " if t != tasks[-1] else "╰ "
                        focus_color: str = quest_focus_color if self.selected_item == t.get_key() else ""
                        t.sentence: Text = self.__str_task(focus_color, t, ligc, ligq, q.is_reachable()) # type: ignore
                        self.__try_add(filtered, matcher, t)
        # verifying if it has any selected item
        if self.items:
            found = False
            for item in self.items:
                if item.get_key() == self.selected_item:
                    found = True
                    break
            if not found:
                self.selected_item = self.items[0].get_key()
                self.reload_sentences()

    def process_collapse_all(self):
        if any([q in self.expanded for q in self.game.quests.keys()]):
            self.expanded = [key for key in self.expanded if key not in self.game.quests.keys()]
        else:
            self.expanded = []

    def process_expand_all(self):
        # if any cluster outside expanded
        expand_clusters = False
        for ckey in self.game.clusters.keys():
            if ckey not in self.expanded:
                expand_clusters = True
        if expand_clusters:
            for ckey in self.game.clusters.keys():
                if ckey not in self.expanded:
                    self.expanded.append(ckey)
        else:
            for qkey in self.game.quests.keys():
                if qkey not in self.expanded:
                    self.expanded.append(qkey)

    def  get_selected_index(self) -> int:
        for i, item in enumerate(self.items):
            if item.key == self.selected_item:
                return i
        return 0

    def get_selected_throw(self) -> TreeItem:
        if len(self.items) > 0:
            index = self.get_selected_index()
            return self.items[index]
        raise IndexError("No item selected")
            


    def set_selected_by_index(self, index: int):
        if index < 0:
            index = 0
        if index >= len(self.items):
            index = len(self.items) - 1
        self.selected_item = self.items[index].key

    def arrow_right(self):
        if len(self.items) == 0:
            return
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

    def walk_left_on_quest(self, index: int):
        while True:
            if index == 0:
                break
            index -= 1
            obj = self.items[index]
            if isinstance(obj, Cluster) or isinstance(obj, Quest) and obj.key in self.expanded:
                break
            if index == 0:
                break
        self.set_selected_by_index(index)

    def walk_left_on_cluster(self, index: int):
        while True:
            if index == 0:
                break
            index -= 1
            obj = self.items[index]
            if isinstance(obj, Cluster) or isinstance(obj, Quest):
                break
            if index == 0:
                break
        self.set_selected_by_index(index)

    def arrow_left(self):
        if len(self.items) == 0:
            return
        index = self.get_selected_index()
        obj = self.items[index]
        if isinstance(obj, Quest):
            if not self.fold(obj):
                self.walk_left_on_quest(index)
            return
        elif isinstance(obj, Cluster):
            if obj.key in self.expanded:
                self.expanded.remove(obj.key)
                for q in obj.get_quests():
                    try:
                        self.expanded.remove(q.key)
                    except ValueError:
                        pass
            else:
                self.walk_left_on_cluster(index)
            return
        elif isinstance(obj, Task):
            while True:
                obj = self.items[index]
                if isinstance(obj, Quest):
                    break
                index -= 1
            self.set_selected_by_index(index)

    def unfold(self, obj: TreeItem) -> bool:
        if isinstance(obj, Quest) and not obj.is_reachable() and not Flags.admin:
            return False
        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.key not in self.expanded:
                self.expanded.append(obj.key)
                if isinstance(obj, Cluster):
                    cluster: Cluster = obj
                    if len(cluster.get_quests()) == 1:
                        self.expanded.append(cluster.get_quests()[0].key)
                return True
        return False

    def fold(self, obj: TreeItem) -> bool:
        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.key in self.expanded:
                self.expanded.remove(obj.key)
                if isinstance(obj, Quest):
                    quest: Quest = obj
                    cluster = self.game.clusters[quest.cluster_key]
                    if len(cluster.get_quests()) == 1:
                        self.expanded.remove(cluster.key)
                        self.selected_item = cluster.key
                return True
        return False

    def toggle(self, obj: Quest | Cluster):
            if not self.fold(obj):
                self.unfold(obj)

    def get_senteces(self, dy: int) -> list[Text]:
        index = self.get_selected_index()
        if len(self.items) < dy:
            self.index_begin = 0
        else:
            if index < self.index_begin:  # subiu na tela
                self.index_begin = index
            elif index >= dy + self.index_begin:  # desceu na tela
                self.index_begin = index - dy + 1

        sentences: list[Text] = []
        for i in range(self.index_begin, len(self.items)):
            sentences.append(self.items[i].sentence)
        return sentences

    def move_up(self):
        if len(self.items) == 0:
            return
        index = self.get_selected_index()
        self.set_selected_by_index(index - 1)

    def move_down(self):
        if len(self.items) == 0:
            return
        index = self.get_selected_index()
        self.set_selected_by_index(min(len(self.items) - 1, index + 1))

    # return a TaskAction
    def get_task_action(self, task: Task) -> tuple[str, str]:
        if task.link_type == Task.Types.VISITABLE_URL:
            return "B", TaskAction.VISITAR
        if task.link_type == Task.Types.STATIC_FILE:
            return "G", TaskAction.EXECUTAR
        
        if not self.is_downloaded_for_lang(task):
            return "Y", TaskAction.BAIXAR
        return "G", TaskAction.EXECUTAR
        
    def is_downloaded_for_lang(self, task: Task):
        folder = task.get_folder()
        lang = self.rep.get_lang()
        if folder is None:
            return False
        drafts = Drafts.load_drafts_only(folder, lang)
        if drafts:
            return True
        return False
        