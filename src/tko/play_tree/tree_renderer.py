from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.tree_item import IsTreeItem
from tko.play_tree.formatter_util import FormatterUtil
from tko.play.flags import Flags
from tko.play_tree.tree_layout import TreeLayout
from tko.play_tree.tree_state import TreeState
from tko.config.settings import Settings
from tko.util.rtext import RText
from tko.util.to_asc import SearchAsc


class TreeRenderer:
    def __init__(self, fmt_util: FormatterUtil, layout: TreeLayout, settings: Settings, flags: Flags, state: TreeState):
        self.fmt_util = fmt_util
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

        output += RText(self.fmt_util.get_task_down_symbol(t)[1], self.fmt_util.get_task_down_symbol(t)[0]) + " "
        output += self.fmt_util.format_percent_1s(t.grader.get_rate_percent()) + " "
        output += RText(self.fmt_util.get_task_help_symbol(t)[1], self.fmt_util.get_task_help_symbol(t)[0]) + " "
        output += RText(self.fmt_util.get_task_path_symbol(t)[1], self.fmt_util.get_task_path_symbol(t)[0]) + " "

        _key_title, _key, _title = self.fmt_util.get_full_title(t, self.layout.key_size)
        title = self.fmt_util.color_task_title(_key, _title)

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
            h, m = self.fmt_util.get_task_hours_minutes(t)
            output += self.fmt_util.format_hours_minutes("g", h, m)

        value = t.grader.full_percent
        output += self.fmt_util.format_percent_3s(value)
        return output

    def render_quest(self, q: Quest, focused: bool) -> RText:
        color = "g" if q.is_reachable() else "y"
        output = q.ui.ligature.set_style(color)
        done, total = q.get_completion()
        output += f" {done:02}/{total:02}"
        star_symbol, percent_text = self.fmt_util.get_start_symbols_and_percent_text(q)
        output += " " + star_symbol + " "

        color = q.ui.is_requirement_color

        title = q.get_full_title(self.flags.panel.is_skills() and self.flags.show_panel.is_true()).add_style(color)
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
            h, m = self.fmt_util.get_quest_time(q)
            output += self.fmt_util.format_hours_minutes("g", h, m)
        output += percent_text

        return output
