from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.tree_item import IsTreeItem
from tko.play_tree.task_formatter import TaskFormatter
from tko.play_tree.quest_formatter import QuestFormatter
from tko.play_tree.time_formatter import TimeFormatter
from tko.play.flags import Flags
from tko.play_tree.tree_layout import TreeLayout
from tko.play_tree.tree_state import TreeState
from tko.play.quest_visibility_service import QuestVisibilityService
from tko.config.settings import Settings
from tko.util.rtext import RText
from tko.util.to_asc import SearchAsc


class TreeRenderer:
    def __init__(
        self,
        task_formatter: TaskFormatter,
        quest_formatter: QuestFormatter,
        time_formatter: TimeFormatter,
        layout: TreeLayout,
        settings: Settings,
        flags: Flags,
        state: TreeState,
    ):
        self.task_formatter = task_formatter
        self.quest_formatter = quest_formatter
        self.time_formatter = time_formatter
        self.layout = layout
        self.settings = settings
        self.flags = flags
        self.state = state
        self.filler = "."

    def mark_search_match(self, text: RText, matcher: SearchAsc):
        pos = matcher.find(text.plain())
        if pos != -1:
            end = pos + len(matcher.pattern)
            text = text.slice(0, pos) + text.slice(pos, end).add_style("X") + text.slice(end)
        return text

    def render(self, item: IsTreeItem, selected_key: str, matcher: SearchAsc) -> RText:
        if isinstance(item, Quest):
            focused = item.basic.full_key == selected_key
            return self.render_quest(item, focused)

        if isinstance(item, Task):
            focused = item.basic.full_key == selected_key
            return self.mark_search_match(self.render_task(item, focused), matcher)

        return RText("")

    def render_task(self, t: Task, focused: bool) -> RText:
        output = RText(" ")
        output += RText(str(t.game.xp), "b") + " "

        output += RText(self.task_formatter.get_task_down_symbol(t)[1], self.task_formatter.get_task_down_symbol(t)[0]) + " "
        output += self.time_formatter.format_percent_1s(t.grader.get_rate_percent()) + " "
        output += RText(self.task_formatter.get_task_help_symbol(t)[1], self.task_formatter.get_task_help_symbol(t)[0]) + " "
        output += RText(self.task_formatter.get_task_path_symbol(t)[1], self.task_formatter.get_task_path_symbol(t)[0]) + " "
        remote_name: str = ""
        if self.layout.use_full_key:
            remote_name = t.basic.remote_name
        _key_title, _key, _title = self.task_formatter.get_task_full_title(
            task=t,
            key_pad=self.layout.key_size,
            remote_name=remote_name,
        )
        title = self.task_formatter.color_task_title(_key, _title)

        focus_color = self.settings.colors.focused_item if focused else ""
        if focused:
            title = title.add_style(focus_color)
        output += title
        if len(output) > self.layout.sentence_cut_size:
            output = output.slice(0, self.layout.sentence_cut_size - 1) + "…"
        else:
            output = output.ljust(self.layout.sentence_cut_size, RText(" ", focus_color))
        output += " "

        if self.flags.show_time.is_true():
            h, m = self.time_formatter.get_task_hours_minutes(t)
            output += self.time_formatter.format_hours_minutes("g", h, m)

        value = t.grader.full_percent
        output += self.time_formatter.format_percent_3s(value)
        return output

    def render_quest(self, q: Quest, focused: bool) -> RText:
        color = "g" if QuestVisibilityService.is_reachable(q) else "y"
        output = q.ui.ligature.set_style(color)
        done, total = q.progress.get_completion()
        output += f" {done:02}/{total:02}"
        star_symbol, percent_text = self.quest_formatter.get_start_symbols_and_percent_text(q)
        output += " " + star_symbol + " "

        color = q.ui.is_requirement_color

        title = self.quest_formatter.get_quest_full_title(
            q,
            self.flags.panel.is_skills() and self.flags.show_panel.is_true(),
        ).add_style(color)
        if focused:
            color = self.settings.colors.focused_item
            title = title.add_style(color)
        output += title
        if len(output) > self.layout.sentence_cut_size:
            output = output.slice(0, self.layout.sentence_cut_size - 1) + "…"
        else:
            output = output.ljust(self.layout.sentence_cut_size, RText(self.filler, color))
        output += " "
        if self.flags.show_time.is_true():
            h, m = self.time_formatter.get_quest_time(q)
            output += self.time_formatter.format_hours_minutes("g", h, m)
        output += percent_text

        return output
