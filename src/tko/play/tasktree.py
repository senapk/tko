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
        self.search_text: str = ""
        self.expanded: list[str] = []
        self.load_all_items()
        self.load_from_rep()
        self.update_tree(admin_mode = Flags.quests.get_value() == "2")
        self.MIN_TITLE_LENGTH = 0
        self.cache_max_title: None | int = None
        self.cache_task_times: dict[str, tuple[int, int]] = {}
        self.reload_sentences()

    def load_all_items(self):
        for c in self.game.clusters.values():
            self.all_items[c.get_db_key()] = c
            for q in c.get_quests():
                self.all_items[q.get_db_key()] = q
                for t in q.get_tasks():
                    self.all_items[t.get_db_key()] = t

    def load_from_rep(self):
        self.expanded: list[str] = [v for v in self.rep.data.expanded]
        self.selected_item = self.rep.data.selected

    def save_on_rep(self):
        self.rep.data.expanded = self.expanded
        # self.rep.set_new_items([x for x in set(self.new_items)])
        self.rep.data.selected = self.selected_item
        tasks: dict[str, str] = {}
        for t in self.game.tasks.values():
            if len(t.info.get_kv()) != 0:
                tasks[t.get_db_key()] = t.save_to_db()
        self.rep.data.tasks = tasks

    def update_tree(self, admin_mode: bool):
        self.game.update_reachable_and_available()
        if not admin_mode:
            reachable_quests = [q.get_db_key() for q in self.game.quests.values() if q.is_reachable()]
            reachable_keys = reachable_quests + list(self.game.clusters.keys())
            for key in self.expanded:
                if key not in reachable_keys:
                    self.expanded.remove(key)

    def get_cluster_title_size(self, cluster: Cluster) -> int:
        return len(cluster.get_database() + ":" + cluster.get_title()) + 3
    
    def get_quest_title_size(self, quest: Quest) -> int:
        return len(quest.get_full_title()) + 5

    def get_task_title_size(self, task: Task) -> int:
        return len(task.get_title()) + 11

    def get_max_title(self) -> int:
        if self.cache_max_title:
            return self.cache_max_title
        
        items: list[int] = []
        for c in self.game.clusters.values():
            if c.get_db_key() in self.game.clusters.keys():
                items.append(self.get_cluster_title_size(c))
                if c.get_db_key() in self.expanded:
                    for q in c.get_quests():
                        items.append(self.get_quest_title_size(q))
                        if q.get_db_key() in self.expanded:
                            for t in q.get_tasks():
                                items.append(self.get_task_title_size(t))

        
        self.cache_max_title = self.MIN_TITLE_LENGTH
        if len(items) > 0:
            self.cache_max_title = max(items)
        self.cache_max_title = max(self.MIN_TITLE_LENGTH, self.cache_max_title)
        return self.cache_max_title

    @staticmethod
    def color_task_title(title: str, color: str) -> Text:
        words = title.split(" ")
        output = Text()
        for i, word in enumerate(words):
            if word.startswith("@") or word.startswith("#") or word.startswith("!"):
                output.addf(color + "g", word)
            elif word.startswith(":"):
                output.addf(color + "y", word)
            elif word.startswith("*"):
                output.addf(color + "c", word)
            elif word.startswith("+"):
                output.addf(color + "c", word)
            else:
                output.addf(color, word)
            if i < len(words) - 1:
                output.addf(color, " ")
        return output

    def format_hours_minutes(self, color: str, hours: int, minutes: int) -> Text:
        output = Text()
        if hours > 0 or minutes > 0:
            output.addf(color, f"{hours:02}h{minutes:02}m ")
        else:
            output.add("┄" * 6 + " ")
        return output

    def get_task_down_symbol(self, t: Task) -> Text.Token:
        down_symbol = symbols.task_to_visit
        if t.link_type == Task.Types.STATIC_FILE:
            down_symbol = symbols.task_local
        if t.link_type == Task.Types.REMOTE_FILE or t.link_type == Task.Types.IMPORT_FILE:
            down_symbol = symbols.task_to_download
            if self.is_downloaded_for_lang(t):
                down_symbol = symbols.task_downloaded
        return down_symbol

    def get_feedback_symbol(self, t: Task) -> Text:
        output = Text()
        if t.info.feedback:
            output.addf("g", symbols.closed_circle)
        elif t.info.rate > 0:
            output.addf("r", symbols.closed_circle)
        else:
            output.addf("", symbols.open_circle)
        return output

    def __str_task(self, focus_color: str, t: Task, lig_cluster: str, lig_quest: str, quest_reachable: bool) -> Text:
        color_aval = "g" if quest_reachable and t.is_reachable() else "y"

        output = Text()
        output.add(" ").addf(color_aval, lig_cluster).add(" ")
        output.addf(color_aval, lig_quest)
        output.add(self.get_task_down_symbol(t)).add(" ")
        rate = t.info.rate // 10
        output.add(t.get_prog_symbol(rate)).add(" ")
        output.add(self.get_feedback_symbol(t))

        in_focus = focus_color != ""
        output.add(self.style.round_l(focus_color) if in_focus else " ")
        color = "" if not in_focus else "k" + focus_color
        output.add(self.color_task_title(t.get_title(), color))
        output.ljust(self.get_max_title(), Text.Token(" ", focus_color))
        output.add(self.style.round_r(focus_color) if in_focus else " ") 

        if Flags.show_time.is_true():
            hours, minutes = self.get_task_hours_minutes(t)
            output.add(self.format_hours_minutes("g", hours, minutes))

        prog = round(t.get_percent())
        output.addf("y", str(prog).rjust(3, " ") + "%")
        return output

    def get_task_hours_minutes(self, task: Task) -> tuple[int, int]:
        if task.get_db_key() in self.cache_task_times:
            return self.cache_task_times[task.get_db_key()]
        logsort = self.rep.logger.tasks.task_dict.get(task.get_db_key(), None)
        if logsort is not None and len(logsort.base_list) > 0:
            delta, _ = logsort.base_list[-1]
            hours = delta.accumulated.seconds // 3600
            minutes = (delta.accumulated.seconds % 3600) // 60
            self.cache_task_times[task.get_db_key()] = (hours, minutes)
            return hours, minutes
        self.cache_task_times[task.get_db_key()] = (0, 0)
        return 0, 0
    
    def __str_quest(self, has_kids: bool, focus_color: str, q: Quest, lig: str) -> Text:
        con = "┄┄"
        n_visible, n_hidden = self.count_visible_hidden_tasks(q)
        if n_visible > 0:
            con = "━─" if n_hidden == 0 else "━┄"
            if q.get_db_key() in self.expanded and has_kids:
                con = "─╮" if n_hidden == 0 else "┄╮"

        color_reachable = "g" if q.is_reachable() else "r"
        if Flags.quests.get_value() == "2":
            for quest in self.game.quests.values():
                if not quest.is_reachable():
                    if q.get_db_key() in quest.requires:
                        color_reachable = "y"
                        break

        output: Text = Text().addf(color_reachable, " " + lig + con)

        in_focus = focus_color != ""

        if focus_color == "":
            item_key = self.selected_item
            if item_key in list(self.game.quests.keys()):
                quest = self.game.quests[item_key]
                if not quest.is_reachable():
                    if q.get_db_key() in quest.requires:
                        focus_color = "y"

        if in_focus:
            output.add(self.style.round_l(focus_color))
        else:
            output.add(" ")

        output.addf(focus_color, q.get_full_title())
        output = output.ljust(self.get_max_title(), Text.Token(".", focus_color))
        output.add(self.style.round_r(focus_color) if in_focus else " ")
        
        if Flags.show_time.is_true():
            hours, minutes = self.get_quest_time(q)
            output.add(self.format_hours_minutes("g", hours, minutes))
        output.add(q.get_resume_by_percent())

        all_tasks_done = True
        for t in q.get_tasks():
            if not t.is_complete():
                all_tasks_done = False
                break
        if all_tasks_done:
            output.add("🌟")

        return output

    def get_quest_time(self, quest: Quest) -> tuple[int, int]:
        hours = 0
        minutes = 0
        for t in quest.get_tasks():
            th, tm = self.get_task_hours_minutes(t)
            hours += th
            minutes += tm
        hours += minutes // 60
        minutes = minutes % 60
        return hours, minutes

    def __str_cluster(self, has_kids: bool, focus_color: str, cluster: Cluster) -> Text:
        output: Text = Text()
        opening = "━─"
        if cluster.get_db_key() in self.expanded and has_kids:
            opening = "─┯"
        color_reachable = "g" if cluster.is_reachable() else "y"
        output.addf(color_reachable, opening)

        color = ""
        if focus_color != "":
            color = "k" + focus_color
        
        if focus_color != "":
            output.add(self.style.round_l(focus_color))
        else:
            output.add(" ")
        
        len_extra = 0
        if Flags.show_time.is_true():
            len_extra = len(self.format_hours_minutes("", 0, 0))

        output = output.addf(color, cluster.get_database() + ":" + cluster.get_title()).ljust(self.get_max_title() + len_extra, Text.Token(".", color))

        if focus_color != "":
            output.add(self.style.round_r(focus_color))
        else:
            output.add(" ")

        output.add(cluster.get_resume_by_percent())


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
            if search.inside(cluster.get_title()):
                matches.add(cluster.get_db_key())
                first = first or cluster.get_db_key()
            for quest in cluster.get_quests():
                if search.inside(quest.get_title()):
                    first = first or quest.get_db_key()
                    matches.add(cluster.get_db_key())
                    matches.add(quest.get_db_key())
                for task in quest.get_tasks():
                    if search.inside(task.get_title()):
                        first = first or task.get_db_key()
                        matches.add(cluster.get_db_key())
                        matches.add(quest.get_db_key())
                        matches.add(task.get_db_key())
        return matches, first

    def __try_add(self, filtered: set[str], matcher: SearchAsc, item: TreeItem):
        if self.search_text == "":
            self.items.append(item)
            return True
        if item.get_db_key() in filtered:
            pos = matcher.find(item.get_sentence().get_str())
            found = pos != -1
            if found:
                for i in range(pos, pos + len(self.search_text)):
                    item.get_sentence().data[i].fmt = "Y"
            self.items.append(item)
            return True
        return False

    def is_hide_tasks(self, task: Task) -> bool:
        if Flags.tasks.get_value() == "1" and task.get_percent() > 99:
            return True
        if Flags.tasks.get_value() == "2" and task.get_percent() > 70:
            return True
        return False

    def remove_empty_quests(self):
        for c in self.game.clusters.values():
            if c.get_db_key() not in self.expanded:
                continue
            for q in c.get_quests():
                if q.get_db_key() not in self.expanded:
                    continue
                visible, _ = self.count_visible_hidden_tasks(q)
                if visible == 0:
                    self.expanded.remove(q.get_db_key())

    def reload_sentences(self):
        self.cache_task_times.clear()
        self.cache_max_title = None # force recalculation of max title size
        self.items = []
        self.remove_empty_quests()
        filtered, _ = self.filter_by_search()
        matcher = SearchAsc(self.search_text)

        hide = Flags.quests.get_value() == "0"

        clusters = [self.game.clusters[key] for key in self.game.clusters.keys() if key in filtered]
        if hide:
            clusters = [c for c in clusters if c.is_reachable()]

        for cluster in clusters:
            quests = [q for q in cluster.get_quests() if q.get_db_key() in self.game.quests.keys() if q.get_db_key() in filtered]
            if hide:
                quests = [q for q in quests if q.is_reachable()]
            focus_color = self.__get_focus_color_cluster(cluster) if self.selected_item == cluster.get_db_key() else ""
            cluster.set_sentence(self.__str_cluster(len(quests) > 0, focus_color, cluster))

            self.__try_add(filtered, matcher, cluster)

            if cluster.get_db_key() not in self.expanded:  # adicionou o cluster, mas não adicione as quests
                continue

            for q in quests:
                tasks =[t for t in q.get_tasks() if t.get_db_key() in filtered]
                if hide:
                    tasks = [t for t in tasks if t.is_reachable()]
                lig = "├" if q != quests[-1] else "╰"
                quest_focus_color: str = self.__get_focus_color_quest(q)
                focus_color = quest_focus_color if self.selected_item == q.get_db_key() else ""
                q.set_sentence(self.__str_quest(len(tasks) > 0, focus_color, q, lig))

                full_task_size = len(tasks)
                tasks = [t for t in tasks if not self.is_hide_tasks(t)]
                filtered_tasks_size = len(tasks)
                has_hidden_tasks = full_task_size != filtered_tasks_size

                self.__try_add(filtered, matcher, q)
                if q.get_db_key() in self.expanded:
                    for t in tasks:
                        if has_hidden_tasks:
                            ligq = "┆ " if t != tasks[-1] else "╰ "
                        else:
                            ligq = "├ " if t != tasks[-1] else "╰ "
                        ligc = "│" if q != quests[-1] else " "
                        focus_color: str = quest_focus_color if self.selected_item == t.get_db_key() else ""
                        t.set_sentence(self.__str_task(focus_color, t, ligc, ligq, q.is_reachable()))
                        # if self.is_hide_tasks(t):
                        #     continue
                        self.__try_add(filtered, matcher, t)
        # verifying if it has any selected item
        if self.items:
            found = False
            for item in self.items:
                if item.get_db_key() == self.selected_item:
                    found = True
                    break
            if not found:
                self.selected_item = self.items[0].get_db_key()
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
            if item.get_db_key() == self.selected_item:
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
        self.selected_item = self.items[index].get_db_key()

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
            if isinstance(obj, Cluster) or isinstance(obj, Quest) and obj.get_db_key() in self.expanded:
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
            if obj.get_db_key() in self.expanded:
                self.expanded.remove(obj.get_db_key())
                for q in obj.get_quests():
                    try:
                        self.expanded.remove(q.get_db_key())
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

    def is_admin_mode(self) -> bool:
        return Flags.quests.get_value() == "2"

    def unfold(self, obj: TreeItem) -> bool:
        if isinstance(obj, Quest) and not obj.is_reachable() and not self.is_admin_mode():
            return False
        if isinstance(obj, Quest):
            visible, _ = self.count_visible_hidden_tasks(obj)
            if visible == 0:
                return False
        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.get_db_key() not in self.expanded:
                self.expanded.append(obj.get_db_key())
                if isinstance(obj, Cluster):
                    cluster: Cluster = obj
                    if len(cluster.get_quests()) == 1:
                        self.expanded.append(cluster.get_quests()[0].get_db_key())
                return True
        return False

    def count_visible_hidden_tasks(self, quest: Quest) -> tuple[int, int]:
        visible = 0
        hidden = 0
        for t in quest.get_tasks():
            if not self.is_hide_tasks(t):
                visible += 1
            else:
                hidden += 1
        return visible, hidden

    def fold(self, obj: TreeItem) -> bool:
        if isinstance(obj, Quest) or isinstance(obj, Cluster):
            if obj.get_db_key() in self.expanded:
                self.expanded.remove(obj.get_db_key())
                if isinstance(obj, Quest):
                    quest: Quest = obj
                    cluster = self.game.clusters[quest.cluster_key]
                    if len(cluster.get_quests()) == 1:
                        self.expanded.remove(cluster.get_db_key())
                        self.selected_item = cluster.get_db_key()
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
            sentences.append(self.items[i].get_sentence())
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
        try:
            folder = task.get_folder_try()
        except:
            return False
        lang = self.rep.data.lang
        drafts = Drafts.load_drafts_only(folder, lang)
        if drafts:
            return True
        return False
        