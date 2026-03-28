
from tko.settings.repository import Repository
from tko.util.text import Text
from tko.util.to_asc import SearchAsc
from tko.play.flags import Flags
from tko.game.quest import Quest
from tko.game.task import Task
from tko.play.border import Border
from tko.down.drafts import Drafts
from tko.settings.settings import Settings
from tko.play.floating_manager import FloatingManager
from tko.util.symbols import Symbols
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
        self.filler = "·"
        self.index_begin: int = 0
        self.search_text: str = ""
        self.expanded: set[str] = set()
        self.load_all_items()
        self.load_from_rep()
        self.update_tree(admin_mode = Flags.inbox.get_value() == Flags.inbox_all)
        self.MIN_TITLE_LENGTH = 50
        self.cache_max_title: None | int = None
        self.cache_task_times: dict[str, tuple[int, int]] = {}
        self.max_key_size: None | int = None
        self.reload_sentences()

    def get_max_key_size(self):
        keys_visible: list[str] = []
        if self.max_key_size is None:
            for q in self.game.quests.values():
                if not q.get_full_key() in self.expanded:
                    continue
                for t in q.get_tasks():
                    keys_visible.append(t.get_key())
        if len(keys_visible) == 0:
            return 10
        return max([len(k) for k in keys_visible])
    
    def get_max_quest_itens_key_size(self, quest_key: str):
        q = self.all_items.get(quest_key, None)
        if q is None or not isinstance(q, Quest):
            return 10
        keys: list[int] = [len(task.get_key()) for task in q.get_tasks()]
        if len(keys) == 0:
            return 10
        return max(keys)

    def load_all_items(self):
        for q in self.game.quests.values():
            self.all_items[q.get_full_key()] = q
            for t in q.get_tasks():
                self.all_items[t.get_full_key()] = t

    def load_from_rep(self):
        self.expanded = set(self.rep.data.expanded)
        self.selected_item = self.rep.data.selected

    def save_on_rep(self):
        self.rep.data.expanded = [x for x in self.expanded if x in self.game.quests.keys()]
        # self.rep.set_new_items([x for x in set(self.new_items)])
        self.rep.data.selected = self.selected_item
        tasks: dict[str, str] = {}
        for t in self.game.tasks.values():
            if len(t.info.get_kv()) != 0:
                tasks[t.get_full_key()] = t.save_to_db()
        self.rep.data.tasks = tasks

    def update_tree(self, admin_mode: bool):
        self.game.update_reachable_and_available()
        if not admin_mode:
            reachable_keys = [q.get_full_key() for q in self.game.quests.values() if q.is_reachable()]
            self.expanded = set(x for x in self.expanded if x in reachable_keys)

    def get_quest_title_size(self, quest: Quest) -> int:
        return len(quest.get_full_title()) + 6

    def get_task_title_size(self, task: Task) -> int:
        return len(task.get_full_title(self.get_max_key_size())) + 22

    def get_max_title(self) -> int:
        if self.cache_max_title:
            return self.cache_max_title
        
        items: list[int] = []
        for q in self.game.quests.values():
            items.append(self.get_quest_title_size(q))
            if q.get_full_key() in self.expanded:
                for t in q.get_tasks():
                    items.append(self.get_task_title_size(t))
        
        self.cache_max_title = self.MIN_TITLE_LENGTH
        if len(items) > 0:
            self.cache_max_title = max(items)
        self.cache_max_title = max(self.MIN_TITLE_LENGTH, self.cache_max_title)
        return self.cache_max_title

    # def get_total_width(self) -> int:
    #     width = self.get_max_title()
    #     if Flags.show_time.is_true():
    #         width += len(self.format_hours_minutes("", 0, 0))
    #     width += 7 # for percent and symbols
    #     return max(width, self.MIN_TITLE_LENGTH + 10)

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

    def get_task_down_symbol(self, t: Task) -> tuple[str, str]:
        if t.is_link():
            if t.info.feedback:
                return ("g", Symbols.task_view)
            return ("", Symbols.task_view)

        if not t.is_import_type():
            if t.info.feedback:
                return ("g", Symbols.right_triangle_filled)
            return ("", Symbols.right_triangle_void)
        if self.is_downloaded_for_lang(t):
            if t.info.feedback:
                return ("g", Symbols.down_triangle_filled)
            return ("", Symbols.down_triangle_void)
        if t.info.feedback:
            return ("g", Symbols.up_triangle_filled)
        return ("", Symbols.up_triangle_void)

    def get_task_path_symbol(self, t: Task) -> tuple[str, str]:
        if t.task_path == Task.TaskPath.MAIN:
            return ("y", Symbols.star_filled)
        return ("", Symbols.star_void)
    
    def get_task_help_symbol(self, t: Task) -> tuple[str, str]:
        if t.task_help == Task.TaskHelp.FREE:
            return ("g", Symbols.task_reload)
        if t.task_help == Task.TaskHelp.PART:
            return ("y", Symbols.task_reload)
        if t.task_help == Task.TaskHelp.ZERO:
            return ("r", Symbols.task_zero)
        return ("", "")

    def get_task_mode_symbol(self, t: Task) -> tuple[str, str]:
        if t.task_mode == Task.TaskMode.VIEW:
            return ("c", Symbols.task_view)
        if t.task_mode == Task.TaskMode.EDIT:
            return ("c", Symbols.task_edit)
        return ("", Symbols.task_edit)

    def format_percent_1s(self, value: float) -> Text:
        prog = value
        if prog < 0.1:
            return Text().addf("", Symbols.middle_dot)
        if prog > 99:
            return Text().addf("g", Symbols.check)
        return Text().addf("y", str(round(prog / 10)).rjust(1, "0"))

    def format_percent_2s(self, value: float | None) -> Text:
        if value is None:
            return Text().addf("", "--")
        prog = round(value)
        if prog < 0.1:
            return Text().addf("", Symbols.middle_dot + Symbols.middle_dot)
        if prog > 99:
            return Text().addf("g", Text() + "▬▬")
            
        return Text().addf("y", str(prog).rjust(2, "0"))
        
    def get_percent_color(self, value: float) -> str:
        color = "g" if value > 99 else ("y" if value > 49 else "r")
        return color

    def __str_task(self, focus_color: str, t: Task, lig_quest: str, quest_reachable: bool) -> Text:
        color_aval = "g" if quest_reachable and t.is_reachable() else "y"

        output = Text()
        output.addf("b", t.xp)
        output.addf(color_aval, lig_quest)

        output.add(self.get_task_down_symbol(t)).add(" ")
        output.add(self.format_percent_1s(t.get_rate_percent())).add(" ")
        output.add(self.get_task_help_symbol(t)).add(" ")
        output.add(self.get_task_path_symbol(t)).add(" ")

        in_focus = focus_color != ""
        color = "" if not in_focus else "k" + focus_color
        output.add(self.color_task_title(t.get_full_title(self.get_max_quest_itens_key_size(t.quest_key)), color))
        output.ljust(self.get_max_title(), Text.Token(" ", focus_color))

        output.add(Symbols.left_triangle_filled if in_focus else " ")

        if Flags.show_time.is_true():
            hours, minutes = self.get_task_hours_minutes(t)
            output.add(self.format_hours_minutes("g", hours, minutes))
        
        rate = t.get_rate_percent()
        if t.task_help != Task.TaskHelp.FREE and rate > 0:
            rate = rate * t.get_quality_percent() / 100
        if rate > 1:
            color = "g" if rate > 99 else ("y" if rate > 49 else "r")
            output.addf(color, f"{round(rate):>3}%")
        else:
            output.addf("", "----")

        return output
    
    def __str_quest(self, has_kids: bool, focus_color: str, q: Quest) -> Text:
        con = "┄┄"
        n_visible, n_hidden = self.count_visible_hidden_tasks(q)
        if n_visible > 0:
            con = "━─" if n_hidden == 0 else "━┄"
            if q.get_full_key() in self.expanded and has_kids:
                con = "─╮" if n_hidden == 0 else "┄╮"

        color_reachable = "g" if q.is_reachable() else "y"
        output: Text = Text().addf(color_reachable, con).add(" ")

        output.add(Symbols.star_filled)
        output.add(self.format_percent_2s(q.get_percent(include_main=True, include_side=False))).add("|")
        output.add(self.format_percent_2s(q.get_percent(include_main=False, include_side=True)))
        output.add(Symbols.star_void).add(" ")

        in_focus = focus_color != ""

        if focus_color == "":
            item_key = self.selected_item
            if item_key in list(self.game.quests.keys()):
                quest = self.game.quests[item_key]
                if not quest.is_reachable():
                    if q.get_full_key() in quest.requires:
                        focus_color = "y"

        # if in_focus:
            # output.add(self.style.round_l(focus_color))
        title = q.get_full_title()
        if focus_color:
            title.set_bg(focus_color)
    
        output.add(title)
        output = output.ljust(self.get_max_title(), Text.Token(self.filler, focus_color))
        output.add(Symbols.left_triangle_filled if in_focus else " ")
                
        if Flags.show_time.is_true():
            hours, minutes = self.get_quest_time(q)
            output.add(self.format_hours_minutes("g", hours, minutes))

        main_obtained, main_total = q.get_xp(include_main=True, include_side=False)
        side_obtained, _ = q.get_xp(include_main=False, include_side=True)
        if main_total != 0:
            main_rate = round(((main_obtained + side_obtained) * 100.0) / main_total)
            color = "g" if main_rate > 99 else ("y" if main_rate > 49 else "r")
            output.addf(color, f"{main_rate:>3}%")
        else:
            output.addf("", "----")


        return output

    def get_task_hours_minutes(self, task: Task) -> tuple[int, int]:
        if task.get_full_key() in self.cache_task_times:
            return self.cache_task_times[task.get_full_key()]
        logsort = self.rep.logger.tasks.task_dict.get(task.get_full_key(), None)
        if logsort is not None and len(logsort.base_list) > 0:
            delta, _ = logsort.base_list[-1]
            hours = delta.accumulated.seconds // 3600
            minutes = (delta.accumulated.seconds % 3600) // 60
            self.cache_task_times[task.get_full_key()] = (hours, minutes)
            return hours, minutes
        self.cache_task_times[task.get_full_key()] = (0, 0)
        return 0, 0

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

    
    def __get_focus_color_quest(self, item: Quest) -> str:
        if not item.is_reachable():
                return "R"
        return self.settings.colors.focused_item

    def filter_by_search(self) -> tuple[set[str], str | None]:
        matches: set[str] = set()
        search = SearchAsc(self.search_text)
        first: None | str = None
        
        for quest in self.game.quests.values():
            if search.inside(quest.get_title()):
                first = first or quest.get_full_key()
                matches.add(quest.get_full_key())
            for task in quest.get_tasks():
                if search.inside(task.get_title()):
                    first = first or task.get_full_key()
                    matches.add(quest.get_full_key())
                    matches.add(task.get_full_key())
        return matches, first

    def __try_add(self, filtered: set[str], matcher: SearchAsc, item: TreeItem):
        if self.search_text == "":
            self.items.append(item)
            return True
        if item.get_full_key() in filtered:
            pos = matcher.find(item.get_sentence().get_str())
            found = pos != -1
            if found:
                for i in range(pos, pos + len(self.search_text)):
                    item.get_sentence().data[i].fmt = "Y"
            self.items.append(item)
            return True
        return False

    def is_hide_tasks(self, task: Task) -> bool:
        if Flags.inbox.get_value() == Flags.inbox_only and task.task_path == Task.TaskPath.SIDE and not self.is_downloaded_for_lang(task):
            return True
        return False

    def remove_empty_quests(self):
        new_expanded = set(self.expanded)
        for q in self.game.quests.values():
            if q.get_full_key() not in self.expanded:
                continue
            visible, _ = self.count_visible_hidden_tasks(q)
            if visible == 0:
                new_expanded.remove(q.get_full_key())
        self.expanded = new_expanded

    def reload_sentences(self):
        self.cache_task_times.clear()
        self.cache_max_title = None # force recalculation of max title size
        self.items = []
        self.remove_empty_quests()
        filtered, _ = self.filter_by_search()
        matcher = SearchAsc(self.search_text)

        hide: bool = Flags.inbox.get_value() == Flags.inbox_only

        quests = [q for q in self.game.quests.values() if q.get_full_key() in self.game.quests.keys() if q.get_full_key() in filtered]
        if hide:
            quests = [q for q in quests if q.is_reachable()]

        for q in quests:
            tasks =[t for t in q.get_tasks() if t.get_full_key() in filtered]
            if hide:
                tasks = [t for t in tasks if t.is_reachable()]
            quest_focus_color: str = self.__get_focus_color_quest(q)
            focus_color = quest_focus_color if self.selected_item == q.get_full_key() else ""
            q.set_sentence(self.__str_quest(len(tasks) > 0, focus_color, q))

            full_task_size = len(tasks)
            tasks = [t for t in tasks if not self.is_hide_tasks(t)]
            filtered_tasks_size = len(tasks)
            has_hidden_tasks = full_task_size != filtered_tasks_size

            self.__try_add(filtered, matcher, q)
            if q.get_full_key() in self.expanded:
                for t in tasks:
                    if has_hidden_tasks:
                        ligq = "┆ " if t != tasks[-1] else "╰ "
                    else:
                        ligq = "├ " if t != tasks[-1] else "╰ "
                    focus_color: str = quest_focus_color if self.selected_item == t.get_full_key() else ""
                    t.set_sentence(self.__str_task(focus_color, t, ligq, q.is_reachable()))
                    # if self.is_hide_tasks(t):
                    #     continue
                    self.__try_add(filtered, matcher, t)
        # verifying if it has any selected item
        if self.items:
            found = False
            for item in self.items:
                if item.get_full_key() == self.selected_item:
                    found = True
                    break
            if not found:
                self.selected_item = self.items[0].get_full_key()
                self.reload_sentences()

    def process_collapse_all(self):
        if any([q in self.expanded for q in self.game.quests.keys()]):
            self.expanded = set([key for key in self.expanded if key not in self.game.quests.keys()])
        else:
            self.expanded = set()

    def process_expand_all(self):
        # if any cluster outside expanded
        new_expanded = [x for x in self.expanded]
        for qkey in self.game.quests.keys():
            if qkey not in self.expanded:
                new_expanded.append(qkey)
        self.expanded = set(new_expanded)

    def  get_selected_index(self) -> int:
        for i, item in enumerate(self.items):
            if item.get_full_key() == self.selected_item:
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
        self.selected_item = self.items[index].get_full_key()

    def arrow_right(self):
        if len(self.items) == 0:
            return
        index = self.get_selected_index()
        obj = self.items[index]

        if isinstance(obj, Quest):
            if not self.unfold(obj):
                while True:
                    index += 1
                    if index >= len(self.items):
                        break
                    obj = self.items[index]
                    if isinstance(obj, Quest):
                        break
                self.set_selected_by_index(index)
        elif isinstance(obj, Task):
            while True:
                obj = self.items[index]
                if isinstance(obj, Quest):
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
            if isinstance(obj, Quest) and obj.get_full_key() in self.expanded:
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
            if isinstance(obj, Quest):
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
        elif isinstance(obj, Task):
            while True:
                obj = self.items[index]
                if isinstance(obj, Quest):
                    break
                index -= 1
            self.set_selected_by_index(index)

    def is_admin_mode(self) -> bool:
        return Flags.inbox.get_value() == Flags.inbox_all

    def unfold(self, obj: TreeItem) -> bool:
        if isinstance(obj, Quest) and not obj.is_reachable() and not self.is_admin_mode():
            return False
        if isinstance(obj, Quest):
            visible, _ = self.count_visible_hidden_tasks(obj)
            if visible == 0:
                return False
        if isinstance(obj, Quest):
            if obj.get_full_key() not in self.expanded:
                self.expanded.add(obj.get_full_key())
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
        if isinstance(obj, Quest):
            if obj.get_full_key() in self.expanded:
                self.expanded.remove(obj.get_full_key())
                return True
        return False

    def toggle(self, obj: Quest):
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
        if task.is_link():
            return "B", TaskAction.VISITAR
        if task.is_static_type():
            return "G", TaskAction.EXECUTAR
        if not self.is_downloaded_for_lang(task):
            return "Y", TaskAction.BAIXAR
        return "G", TaskAction.EXECUTAR
        
    def is_downloaded_for_lang(self, task: Task):
        folder = task.get_workspace_folder()
        if folder is None:
            return False

        lang = self.rep.data.lang
        drafts = Drafts.load_drafts_only(folder, lang)
        if drafts:
            return True
        return False
        