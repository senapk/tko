
from tko.play.FormatterUtil import FormatterUtil
from tko.settings.repository import Repository
from tko.util.text import Text
from tko.util.to_asc import SearchAsc
from tko.play.flags import Flags
from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.game import Game
from tko.settings.settings import Settings
from tko.game.tree_item import TreeItem

class TreeLayout:
    def __init__(self):
        self.key_size_min = 20
        self.sentence_cut_min_size = 30
        self.sentence_cut_max_size = 80

        self.fixed_task_itens_size = 12
        self.fixed_quest_itens_size = 10
        
        self.key_size: int = 0
        self.sentence_cut_size: int = 0 # 0 if not calculated yet

    def reset(self):
        self.key_size = 0
        self.sentence_cut_size = 0

    def calculate(self, game: Game, flags: Flags, expanded: set[str]):
        if self.sentence_cut_size != 0:
            return
        key_sizes: list[int] = []
        sentence_cut: list[int] = []

        for q in game.quests.values():
            for t in q.get_tasks():
                key_sizes.append(len(t.get_key()))
        self.key_size = max(key_sizes) if key_sizes else self.key_size_min

        for q in game.quests.values():
            sentence_cut.append(len(q.get_full_title(flags.panel.is_skills())) + self.fixed_quest_itens_size)
            for t in q.get_tasks():
                sentence_cut.append(len(t.get_full_title(self.key_size)) + self.fixed_task_itens_size)

        self.sentence_cut_size = max(max(sentence_cut), self.sentence_cut_min_size) if sentence_cut else self.sentence_cut_min_size
        if self.sentence_cut_size > self.sentence_cut_max_size:
            self.sentence_cut_size = self.sentence_cut_max_size

class TreeFilter:
    def __init__(self, inbox_mode: bool, search_text: str):
        self.inbox_mode: bool = inbox_mode
        self.search_text: str = search_text

    def hide_elements(self) -> bool:
        return self.inbox_mode and self.search_text == ""

class TreeState:
    expanded: set[str] = set()
    selected: str = ""
    search: str = ""
    scroll: int = 0

    def ensure_valid_selection(self, items: list[TreeItem]):
        """Garante que selected sempre aponta para um item visível"""
        if not items:
            self.selected = ""
            return

        keys = [i.get_full_key() for i in items]
        if self.selected not in keys:
            self.selected = keys[0]

    def get_selected_index(self, items: list[TreeItem]) -> int:
        for i, item in enumerate(items):
            if item.get_full_key() == self.selected:
                return i
        return 0

    def get_selected_throw(self, items: list[TreeItem]) -> TreeItem:
        for item in items:
            if item.get_full_key() == self.selected:
                return item
        raise IndexError("Selected item not found")

    def move_selection(self, delta: int, items: list[TreeItem]):
        if not items:
            return

        index = self.get_selected_index(items)
        index += delta
        index = max(0, min(index, len(items) - 1))
        self.selected = items[index].get_full_key()

    def update_scroll(self, window_height: int, items: list[TreeItem]):
        """Controla o scroll da tela"""
        if not items:
            self.scroll = 0
            return

        index = self.get_selected_index(items)

        if len(items) <= window_height:
            self.scroll = 0
            return

        if index < self.scroll:
            self.scroll = index
        elif index >= self.scroll + window_height:
            self.scroll = index - window_height + 1

class TreeBuilder:
    def __init__(self, fmt_util: FormatterUtil):
        self.fmt_util = fmt_util
        self.repo = fmt_util.repo

    def filter_by_search(self, game: Game, search_text: str) -> tuple[set[str], str | None]:
        matches: set[str] = set()
        first: str | None = None
        search = SearchAsc(search_text)

        for quest in game.quests.values():
            if search.inside(quest.get_title()):
                first = first or quest.get_full_key()
                matches.add(quest.get_full_key())

            for task in quest.get_tasks():
                if search.inside(task.get_full_title(None)):
                    first = first or task.get_full_key()
                    matches.add(quest.get_full_key())
                    matches.add(task.get_full_key())

        return matches, first

    def select_inbox_enabled(self, game: Game, tf: TreeFilter, fmt_util: FormatterUtil) -> set[str]:
        max_count = 10
        enabled: set[str] = set()
        for q in game.quests.values():
            if not q.is_reachable():
                continue
            enabled.add(q.get_full_key())
            count = 0
            # sort tasks choosing first those that are not 100% completed, then the main tasks, then the others
            tasks = sorted(
                q.get_tasks(),
                key=lambda t: (t.get_rate_percent() != 100, t.task_path != Task.TaskMain.MAIN)
            )
            for t in tasks:
                if t.get_rate_percent() == 100 and t.get_quality_percent() == 100:
                    continue
                if fmt_util.is_downloaded_for_lang(t):
                    enabled.add(t.get_full_key())
                    count += 1
                elif count < max_count:
                    enabled.add(t.get_full_key())
                    count += 1
        return enabled

    def enable_all(self, game: Game) -> set[str]:
        matches: set[str] = set()
        for q in game.quests.values():
            matches.add(q.get_full_key())
            for t in q.get_tasks():
                matches.add(t.get_full_key())
        return matches

    def get_enabled_by_mode(self, game: Game, state: TreeState, tfilter: TreeFilter):
        game.update_reachable_and_available()
        if state.search != "":
            enabled, first_match = self.filter_by_search(game, tfilter.search_text)
            if first_match and state.selected == "":
                state.selected = first_match
        elif self.repo.flags.task_view_mode.is_inbox():
            enabled = self.select_inbox_enabled(game, tfilter, self.fmt_util)
        else:
            enabled = self.enable_all(game)
        return enabled
    
    def set_visible(self, game: Game, enabled: set[str]):
        for q in game.quests.values():
            q.is_requirement_color = ""
            if q.get_full_key() in enabled:
                q.visible = True
            else:
                q.visible = False
            for t in q.get_tasks():
                if t.get_full_key() in enabled:
                    t.visible = True
                else:
                    t.visible = False
        # se entrou em modo busca, seleciona o primeiro match

    def build(self, game: Game, state: TreeState, tfilter: TreeFilter) -> list[TreeItem]:
        enabled = self.get_enabled_by_mode(game, state, tfilter)
        self.set_visible(game, enabled)
        items = self.set_colors_and_ligatures(game, state)
        return items
    
    def set_colors_and_ligatures(self, game: Game, state: TreeState) -> list[TreeItem]:
        items: list[TreeItem] = []
        for q in game.quests.values():
            if not q.visible:
                continue
            # coloring quest requiments for selected quest
            for req in q.required_by_ptr:
                if req.get_full_key() == state.selected:
                    q.is_requirement_color = "y" if req.is_reachable() else "r"
                    break
            items.append(q)
            color = "g" if q.is_reachable() else "y"
            tasks: list[Task] = [t for t in q.get_tasks() if t.visible ]
            has_hidden = len(tasks) != len(q.get_tasks())
            if q.get_full_key() not in state.expanded:
                q.ligature = Text("┅┄", color) if has_hidden else Text("━─", color)
                continue
            q.ligature = Text("┅┅", color) if has_hidden else Text("━━", color)
            for t in tasks:
                items.append(t)
        return items
    
class TreeRenderer:
    def __init__(self, fmt_util: FormatterUtil, layout: TreeLayout, settings: Settings, flags: Flags, state: TreeState):
        self.fmt_util = fmt_util
        self.layout = layout
        self.settings = settings
        self.flags = flags
        self.state = state
        self.filler = "."

    def mark_search_match(self, text: Text, matcher: SearchAsc):
            pos = matcher.find(text.get_str())
            if pos != -1:
                for i in range(pos, pos + len(matcher.pattern)):
                    text.data[i].fmt += "X"
            return text

    def render(self, item: TreeItem, selected_key: str, matcher: SearchAsc) -> Text:
        if isinstance(item, Quest):
            focused = item.get_full_key() == selected_key
            return self.render_quest(item, focused)

        if isinstance(item, Task):
            focused = item.get_full_key() == selected_key
            return self.mark_search_match(self.render_task(item, focused), matcher)

        return Text("")


    def render_task(self, t: Task, focused: bool) -> Text:
        output = Text().add(" ")
        # output.add(" ").add(t.ligature)
        output.addf("b", t.xp).add(" ")

        output.add(self.fmt_util.get_task_down_symbol(t)).add(" ")
        output.add(self.fmt_util.format_percent_1s(t.get_rate_percent())).add(" ")
        output.add(self.fmt_util.get_task_help_symbol(t)).add(" ")
        output.add(self.fmt_util.get_task_path_symbol(t)).add(" ")

        title = self.fmt_util.color_task_title( t.get_full_title(self.layout.key_size) )

        focus_color = self.settings.colors.focused_item if focused else ""
        if focused:
            title.add_style(focus_color)
        output.add(title)
        if len(output) > self.layout.sentence_cut_size:
            output = output.slice(0, self.layout.sentence_cut_size - 1).add("…")
        else:
            output.ljust(self.layout.sentence_cut_size, Text.Token(" ", focus_color))
        output.add(" ")

        if self.flags.show_time.is_true():
            h, m = self.fmt_util.get_task_hours_minutes(t)
            output.add(self.fmt_util.format_hours_minutes("g", h, m))

        value = t.get_rate_percent() * t.get_quality_percent() / 100
        output.add(self.fmt_util.format_percent_3s(value))
        return output

    def render_quest(self, q: Quest, focused: bool) -> Text:
        color = "g" if q.is_reachable() else "y"
        output = Text()
        output.addf(color, q.ligature)
        done, total = q.get_completion()
        output.add(f" {done:02}/{total:02}")
        star_symbol, percent = self.fmt_util.get_start_symbols_and_percent_quest(q)
        output.add(" ").add(star_symbol).add(" ")

        color = q.is_requirement_color

        title = q.get_full_title(self.flags.panel.is_skills() and self.flags.show_panel.is_true()).add_style(color)
        if focused:
            color = self.settings.colors.focused_item
            title.add_style(color)
        output.add(title)
        if len(output) > self.layout.sentence_cut_size:
            output = output.slice(0, self.layout.sentence_cut_size - 1).add("…")
        else:
            output.ljust(self.layout.sentence_cut_size, Text.Token(self.filler, color))
        output.add(" ")
        if self.flags.show_time.is_true():
            h, m = self.fmt_util.get_quest_time(q)
            output.add(self.fmt_util.format_hours_minutes("g", h, m))
        output.add(percent)

        return output
    

class TreeNavigator:
    def move_up(self, state: TreeState, items: list[TreeItem]):
        state.move_selection(-1, items)

    def move_down(self, state: TreeState, items: list[TreeItem]):
        state.move_selection(+1, items)

    def toggle(self, state: TreeState, items: list[TreeItem]):
        """Expande/contrai se for quest"""
        if not items:
            return

        index = state.get_selected_index(items)
        item = items[index]

        if isinstance(item, Quest):
            key = item.get_full_key()
            if key in state.expanded:
                state.expanded.remove(key)
            else:
                state.expanded.add(key)

    def right(self, state: TreeState, items: list[TreeItem]):
        if not items:
            return

        index = state.get_selected_index(items)
        item = items[index]

        # Se for quest → expandir
        if isinstance(item, Quest):
            key = item.get_full_key()
            if key not in state.expanded:
                state.expanded.add(key)
                return

            # já expandido → ir para próxima quest
            index += 1
            while index < len(items):
                if isinstance(items[index], Quest):
                    state.selected = items[index].get_full_key()
                    return
                index += 1
            return

        # Se for task → pular para próxima quest
        if isinstance(item, Task):
            while index < len(items):
                if isinstance(items[index], Quest):
                    state.selected = items[index].get_full_key()
                    return
                index += 1

    def left(self, state: TreeState, items: list[TreeItem]):
        if not items:
            return

        index = state.get_selected_index(items)
        item = items[index]

        # Se for quest → contrair ou subir
        if isinstance(item, Quest):
            key = item.get_full_key()

            if key in state.expanded:
                state.expanded.remove(key)
                return

            # subir para quest anterior expandida
            index -= 1
            while index >= 0:
                if isinstance(items[index], Quest):
                    state.selected = items[index].get_full_key()
                    return
                index -= 1

        # Se for task → voltar para quest pai
        if isinstance(item, Task):
            while index >= 0:
                if isinstance(items[index], Quest):
                    state.selected = items[index].get_full_key()
                    return
                index -= 1

class TreeRepository:
    def __init__(self, repo: Repository, game: Game):
        self.repo = repo
        self.game = game

    def load_state(self, state: TreeState):
        state.expanded = set(self.repo.data.expanded)
        state.selected = self.repo.data.selected

    def save_state(self, state: TreeState):
        # salvar expanded (somente quests válidas)
        self.repo.data.expanded = [
            x for x in state.expanded
            if x in self.game.quests.keys()
        ]

        # salvar selecionado
        self.repo.data.selected = state.selected


class TaskTree:
    def __init__(self, settings: Settings, repo: Repository):
        self.game = repo.game
        self.repo = repo
        self.settings = settings
        self.state = TreeState()
        self.layout = TreeLayout()
        self.fmt_util = FormatterUtil(settings, repo)
        self.builder = TreeBuilder(self.fmt_util)
        self.renderer = TreeRenderer(self.fmt_util, self.layout, settings, repo.flags, self.state)
        self.navigator = TreeNavigator()
        self.repository = TreeRepository(repo, self.game)

        # loading configs
        self.state.expanded = set(self.repo.data.expanded)
        self.state.selected = self.repo.data.selected

        self.items: list[TreeItem] = []
        # self.lines: list[Text] = []

    def recalculate_layout(self):
        self.layout.reset

    def save_state(self):
        self.repository.save_state(self.state)

    def filter_by_search(self) -> tuple[set[str], str | None]:
        return self.builder.filter_by_search(self.game, self.state.search)

    def get_selected_throw(self) -> TreeItem:
        return self.state.get_selected_throw(self.items)
    
    def get_selected_index(self) -> int:
        return self.state.get_selected_index(self.items)

    def toggle(self):
        self.navigator.toggle(self.state, self.items)

    def move_up(self):
        self.navigator.move_up(self.state, self.items)
        # self.update()
    
    def move_down(self):
        self.navigator.move_down(self.state, self.items)
        # self.update()

    def move_right(self):
        self.navigator.right(self.state, self.items)
        # self.update()

    def move_left(self):
        self.navigator.left(self.state, self.items)
        # self.update()

    def get_visible_sentences(self, height: int) -> list[Text]:
        self.state.update_scroll(height, self.items)
        visible_items = self.items[
            self.state.scroll : self.state.scroll + height
        ]
        return self.get_rendered_items(visible_items)
    
    def get_rendered_items(self, items: list[TreeItem] | None = None) -> list[Text]:
        if items is None:
            items = self.items
        matcher = SearchAsc(self.state.search)
        return [
            self.renderer.render(item, self.state.selected, matcher)
            for item in items
        ]
    
    def update(self, force_view_all: bool = False):
        tree_filter = TreeFilter(
            inbox_mode=self.repo.flags.task_view_mode.is_inbox() and not force_view_all,
            search_text=self.state.search
        )
        self.items = self.builder.build(self.game, self.state, tree_filter)
        self.state.ensure_valid_selection(self.items)
        self.layout.calculate(self.game, self.repo.flags, self.state.expanded)

    def collapse_all(self):
        self.state.expanded.clear()
        # self.update()

    def expand_all(self):
        for q in self.game.quests.values():
            self.state.expanded.add(q.get_full_key())
        # self.update()
