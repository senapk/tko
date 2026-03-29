
from tko.play.FormatterUtil import FormatterUtil
from tko.settings.repository import Repository
from tko.util.text import Text
from tko.util.to_asc import SearchAsc
from tko.play.flags import Flags
from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.game import Game
from tko.settings.settings import Settings
from tko.util.symbols import Symbols
from tko.game.tree_item import TreeItem

class TreeLayout:
    def __init__(self):
        self.max_title: int = 50
        self.max_key_size: int = 50

    def calculate(self, game: Game, flags: Flags, expanded: set[str]):
        key_sizes: list[int] = []
        title_sizes: list[int] = []

        for q in game.quests.values():
            title_sizes.append(len(q.get_full_title(flags.panel.is_skills())) + 5)

            if q.get_full_key() in expanded:
                for t in q.get_tasks():
                    key_sizes.append(len(t.get_key()))
                    title_sizes.append(len(t.get_full_title(None)) + 1)

        self.max_key_size = max(key_sizes) if key_sizes else 10
        self.max_title = max(title_sizes) if title_sizes else 10

class TreeFilter:
    def __init__(self, inbox_mode: bool, search_text: str):
        self.inbox_mode: bool = inbox_mode
        self.search_text: str = search_text

    def hide_unreachable(self) -> bool:
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

    def filter_items(
        self,
        game: Game,
        search_text: str
    ) -> tuple[set[str], str | None]:
        matches: set[str] = set()
        first: str | None = None
        search = SearchAsc(search_text)

        for quest in game.quests.values():
            if search.inside(quest.get_title()):
                first = first or quest.get_full_key()
                matches.add(quest.get_full_key())

            for task in quest.get_tasks():
                if search.inside(task.get_title()):
                    first = first or task.get_full_key()
                    matches.add(quest.get_full_key())
                    matches.add(task.get_full_key())

        return matches, first

    def add_if_match(
        self,
        items: list[TreeItem],
        item: TreeItem,
        filtered: set[str],
        matcher: SearchAsc,
        search_text: str
    ):
        if search_text == "":
            items.append(item)
            return

        if item.get_full_key() in filtered:
            pos = matcher.find(item.get_sentence().get_str())
            if pos != -1:
                for i in range(pos, pos + len(search_text)):
                    item.get_sentence().data[i].fmt = "Y"

            items.append(item)

    def remove_empty_quests(
        self,
        game: Game,
        expanded: set[str]
    ) -> set[str]:
        new_expanded = set(expanded)

        for q in game.quests.values():
            if q.get_full_key() not in expanded:
                continue

            visible, _ = self.fmt_util.count_visible_hidden_tasks(q)
            if visible == 0:
                new_expanded.remove(q.get_full_key())

        return new_expanded

    def filter_by_search(self, game: Game, search_text: str) -> tuple[set[str], str | None]:
        matches: set[str] = set()
        first: str | None = None

        if search_text == "":
            # sem busca → tudo visível
            for q in game.quests.values():
                matches.add(q.get_full_key())
                for t in q.get_tasks():
                    matches.add(t.get_full_key())
            return matches, None

        search = SearchAsc(search_text)

        for quest in game.quests.values():
            if search.inside(quest.get_title()):
                first = first or quest.get_full_key()
                matches.add(quest.get_full_key())

            for task in quest.get_tasks():
                if search.inside(task.get_title()):
                    first = first or task.get_full_key()
                    matches.add(quest.get_full_key())
                    matches.add(task.get_full_key())

        return matches, first

    def build(self, game: Game, state: TreeState, flt: TreeFilter) -> list[TreeItem]:
        items: list[TreeItem] = []

        filtered, first_match = self.filter_by_search(game, flt.search_text)

        # se entrou em modo busca, seleciona o primeiro match
        if first_match and state.selected == "":
            state.selected = first_match

        hide_unreachable: bool = flt.hide_unreachable()

        for q in game.quests.values():
            if q.get_full_key() not in filtered:
                continue

            if hide_unreachable and not q.is_reachable():
                continue

            items.append(q)

            if q.get_full_key() not in state.expanded:
                continue

            tasks = [
                t for t in q.get_tasks()
                if t.get_full_key() in filtered
            ]

            if hide_unreachable:
                tasks = [t for t in tasks if t.is_reachable()]

            tasks = [t for t in tasks if not self.fmt_util.is_hide_tasks(t)]

            for t in tasks:
                items.append(t)

        return items
    
class TreeRenderer:
    def __init__(self, fmt_util: FormatterUtil, layout: TreeLayout, settings: Settings, flags: Flags):
        self.fmt_util = fmt_util
        self.layout = layout
        self.settings = settings
        self.flags = flags
        self.filler = "·"

    def render(self, item: TreeItem, selected_key: str, quest_reachable: bool=True, lig: str="  ") -> Text:
        if isinstance(item, Quest):
            focused = item.get_full_key() == selected_key
            return self.render_quest(item, focused)

        if isinstance(item, Task):
            focused = item.get_full_key() == selected_key
            return self.render_task(item, focused, lig, quest_reachable)

        return Text("")

    def render_task(self, t: Task, focused: bool, lig_quest: str, quest_reachable: bool) -> Text:
        color_aval = "g" if quest_reachable and t.is_reachable() else "y"

        output = Text()
        output.addf("b", t.xp)
        output.addf(color_aval, lig_quest)

        output.add(self.fmt_util.get_task_down_symbol(t)).add(" ")
        output.add(self.fmt_util.format_percent_1s(t.get_rate_percent())).add(" ")
        output.add(self.fmt_util.get_task_help_symbol(t)).add(" ")
        output.add(self.fmt_util.get_task_path_symbol(t)).add(" ")

        focus_color = self.settings.colors.focused_item if focused else ""
        output.add(
            self.fmt_util.color_task_title(
                t.get_full_title(self.layout.max_key_size),
                focus_color
            )
        )

        output.ljust(self.layout.max_title, Text.Token(" ", focus_color))
        output.add(Symbols.left_triangle_filled if focused else " ")

        if self.flags.show_time.is_true():
            h, m = self.fmt_util.get_task_hours_minutes(t)
            output.add(self.fmt_util.format_hours_minutes("g", h, m))

        return output

    def render_quest(self, q: Quest, focused: bool) -> Text:
        color = "g" if q.is_reachable() else "y"
        output = Text().addf(color, "━━ ")

        output.add(Symbols.star_filled)
        output.add(self.fmt_util.format_percent_2s(q.get_percent(True, False))).add("|")
        output.add(self.fmt_util.format_percent_2s(q.get_percent(False, True)))
        output.add(Symbols.star_void).add(" ")

        title = q.get_full_title(self.flags.panel.is_skills())
        if focused:
            title.set_bg(self.settings.colors.focused_item)

        output.add(title)
        output.ljust(self.layout.max_title, Text.Token(self.filler))
        output.add(Symbols.left_triangle_filled if focused else " ")

        if self.flags.show_time.is_true():
            h, m = self.fmt_util.get_quest_time(q)
            output.add(self.fmt_util.format_hours_minutes("g", h, m))

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

        # salvar tasks com info
        tasks: dict[str, str] = {}
        for t in self.game.tasks.values():
            if len(t.info.get_kv()) != 0:
                tasks[t.get_full_key()] = t.save_to_db()

        self.repo.data.tasks = tasks

class TaskTree:
    def __init__(self, settings: Settings, repo: Repository):
        self.game = repo.game
        self.repo = repo
        self.settings = settings
        self.state = TreeState()
        self.layout = TreeLayout()
        self.fmt_util = FormatterUtil(settings, repo)
        self.builder = TreeBuilder(self.fmt_util)
        self.renderer = TreeRenderer(self.fmt_util, self.layout, settings, repo.flags)
        self.navigator = TreeNavigator()
        self.repository = TreeRepository(repo, self.game)

        self.items: list[TreeItem] = []
        self.lines: list[Text] = []

    def save_state(self):
        self.repository.save_state(self.state)
        for t in self.game.tasks.values():
            if t.is_import_type() or t.is_link():
                self.repository.repo.data.tasks[t.get_full_key()] = t.save_to_db()

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
        self.update()
    
    def move_down(self):
        self.navigator.move_down(self.state, self.items)
        self.update()

    def move_right(self):
        self.navigator.right(self.state, self.items)
        self.update()

    def move_left(self):
        self.navigator.left(self.state, self.items)
        self.update()

    def get_visible_sentences(self, height: int) -> list[Text]:
        self.state.update_scroll(height, self.items)

        visible_items = self.items[
            self.state.scroll : self.state.scroll + height
        ]

        return [
            self.renderer.render(item, self.state.selected)
            for item in visible_items
        ]

    def update(self, force_view_all: bool = False):
        tree_filter = TreeFilter(
            inbox_mode=self.repo.flags.task_view_mode.is_inbox() and not force_view_all,
            search_text=self.state.search
        )

        self.items = self.builder.build(self.game, self.state, tree_filter)

        self.state.ensure_valid_selection(self.items)

        self.layout.calculate(self.game, self.repo.flags, self.state.expanded)

        self.lines = [
            self.renderer.render(item, self.state.selected)
            for item in self.items
        ]

    def expand_all(self):
        for q in self.game.quests.values():
            self.state.expanded.add(q.get_full_key())
        self.update()

    def key_up(self):
        self.navigator.move_up(self.state, self.items)
        self.update()

    def key_down(self):
        self.navigator.move_down(self.state, self.items)
        self.update()

    def key_left(self):
        self.navigator.left(self.state, self.items)
        self.update()

    def key_right(self):
        self.navigator.right(self.state, self.items)
        self.update()

    def key_enter(self):
        # self.navigator.toggle(self.state, self.items)
        self.update()