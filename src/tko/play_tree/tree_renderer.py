from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.tree_item import IsTreeItem
from tko.play_tree.task_formatter import TaskFormatter
from tko.play_tree.quest_formatter import QuestFormatter
from tko.play_tree.time_formatter import TimeFormatter
from tko.config.flags import Flags
from tko.play_tree.tree_layout import TreeLayout
from tko.play_tree.tree_state import TreeState
from tko.play.quest_visibility_service import QuestVisibilityService
from tko.config.settings import Settings
from tko.util.rt import RT, RBuffer
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

    def mark_search_match(self, text: RT, matcher: SearchAsc):
        pos = matcher.find(text.plain())
        if pos != -1:
            end = pos + len(matcher.pattern)
            text = text.slice(0, pos) + text.slice(pos, end).add_style("X") + text.slice(end)
        return text

    def render(self, item: IsTreeItem, selected_key: str, matcher: SearchAsc) -> RT:
        if isinstance(item, Quest):
            focused = item.basic.full_key == selected_key
            return self.render_quest(item, focused)

        if isinstance(item, Task):
            focused = item.basic.full_key == selected_key
            return self.mark_search_match(self.render_task(item, focused), matcher)

        return RT("")

    def render_task(self, t: Task, focused: bool) -> RT:
        head = RBuffer()
        head.add(" ")
        head.add(str(t.game.xp), "y")
        head.add(" ")
        down_style, down_text = self.task_formatter.get_task_down_symbol(t)
        head.add(down_text, down_style)
        head.add(" ")
        help_style, help_text = self.task_formatter.get_task_help_symbol(t)
        head.add(help_text, help_style)
        head.add(" ")
        head.add(t.game.tier_symbol)
        head.add(">" if focused else " ")

        output = head.to_rt()
        remote_name: str = ""
        if self.layout.use_full_key:
            remote_name = t.basic.remote_name
        _, _key, _title = self.task_formatter.get_task_full_title(
            task=t,
            key_pad=self.layout.key_size,
            remote_name=remote_name,
        )
        title = self.task_formatter.color_task_title(_key, _title)

        focus_color = self.settings.colors.focused_item if focused else ""
        # focus_color = ""
        if focused:
            title = title.add_style(focus_color)
        output += title
        if len(output) > self.layout.sentence_cut_size:
            output = output.slice(0, self.layout.sentence_cut_size - 1) + "…"
        else:
            output = output.ljust(self.layout.sentence_cut_size, RT(" ", focus_color))
        tail = RBuffer().add(output).add(" ")

        tail.add(self.time_formatter.format_percent_1s(t.grader.get_rate_percent())).add(" ")
        value = t.grader.full_percent
        tail.add(self.time_formatter.format_percent_3s(value))
        if self.flags.show_time.is_true():
            h, m = self.time_formatter.get_task_hours_minutes(t)
            tail.add(" ").add(self.time_formatter.format_hours_minutes("g", h, m))
        return tail.to_rt()

    def render_quest(self, q: Quest, focused: bool) -> RT:
        color = "g" if QuestVisibilityService.is_reachable(q) else "y"
        body = RBuffer().add(q.ui.ligature.set_style(color))
        done, goal, _ = q.progress.get_obtained_goal_available()
        done = round(done)
        goal = round(goal)
        body.add(f" {done:02}/{goal:02}")
        
        body.add(">" if focused else " ")

        color = q.ui.is_requirement_color

        title = self.quest_formatter.get_quest_full_title(
            q,
            self.flags.panel.is_skills() and self.flags.show_panel.is_true(),
        ).add_style(color)
        if focused:
            color = self.settings.colors.focused_item
            title = title.add_style(color)
        output = body.add(title).to_rt()
        
        if len(output) > self.layout.sentence_cut_size:
            output = output.slice(0, self.layout.sentence_cut_size - 1) + "…"
        else:
            output = output.ljust(self.layout.sentence_cut_size, RT(self.filler, color))
        tail = RBuffer().add(output).add("   ")
        percent_text = self.quest_formatter.get_percent_text(q)
        tail.add(percent_text)
        if self.flags.show_time.is_true():
            h, m = self.time_formatter.get_quest_time(q)
            tail.add(" ").add(self.time_formatter.format_hours_minutes("g", h, m))

        return tail.to_rt()
