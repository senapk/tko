from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.tree_item import IsTreeItem
from tko.play_tree.task_formatter import TaskFormatter
from tko.play_tree.quest_formatter import QuestFormatter
from tko.play_tree.time_formatter import TimeFormatter
from tko.config.flags import Flags
from tko.play_tree.tree_layout import TreeLayout
from tko.play_tree.tree_state import TreeState
from tko.config.settings import Settings
from tko.util.rbuffer import RBuffer
from tko.util.rt import RT
from tko.util.to_asc import SearchAsc
from tko.game.xp_display import format_task_xp
from tko.util.symbols import Symbols

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
        status = RBuffer()
        status.add(f"{format_task_xp(t.xp):>3}", "y")
        pinned = t.basic.full_key in self.state.pinned
        status.add(" ★ " if pinned else " ☆ ", "y" if pinned else "")
        if self.flags.show_time.is_true():
            h, m = self.time_formatter.get_task_hours_minutes(t)
            status.add(self.time_formatter.format_hours_minutes("g", h, m))
        status.add(self.time_formatter.format_percent_3s(t.grader.full_percent)).add(" ")

        head = RBuffer()
        # XP has a fixed three-cell column, while preserving its established
        # one-decimal representation for values below ten.
        source, evaluation = self.task_formatter.get_task_source_eval_symbols(t)
        feedback = Symbols.success if t.info.feedback else Symbols.failure
        head.add(source, "c").add(" ").add(evaluation, "m").add(" ").add(feedback, "g" if t.info.feedback else "")
        head.add(" ")

        if self.layout.insert_quest_keys:
            key = t.quest_key
            if "@" in key:
                key = key.split("@")[1]
            head.add(f" #{key:<{self.layout.quest_key_pad}} ", "b")

        output = head.to_rt()
        source_name: str = ""
        if self.layout.use_full_key:
            source_name = t.basic.source_name

        _, _key, _title = self.task_formatter.get_task_full_title(
            task=t,
            key_pad=self.layout.task_key_pad,
            source_name=source_name,
        )
        title = self.task_formatter.color_task_title(_key, _title)

        output += title
        if len(output) > self.layout.sentence_cut_size:
            output = output.slice(0, self.layout.sentence_cut_size - 1) + "…"
        else:
            output = output.ljust(self.layout.sentence_cut_size, RT(" "))
        return status.to_rt() + output

    def render_quest(self, q: Quest, focused: bool) -> RT:
        # The expand/collapse marker is provided by Textual's Tree. Keep the
        # quest label to its metadata and name so the order is predictable.
        body = RBuffer()

        color = q.ui.is_requirement_color

        title = self.quest_formatter.get_quest_full_title(
            q,
            self.flags.panel.is_skills(),
        ).add_style(color)
        output = body.add(title).to_rt()
        
        if len(output) > self.layout.sentence_cut_size:
            output = output.slice(0, self.layout.sentence_cut_size - 1) + "…"
        else:
            output = output.ljust(self.layout.sentence_cut_size, RT(" ", color))
        completed, total = q.progress.get_completion()
        status = RBuffer().add(f"{completed:02}/{total:02}")
        if self.flags.show_time.is_true():
            h, m = self.time_formatter.get_quest_time(q)
            status.add(" ").add(self.time_formatter.format_hours_minutes("g", h, m))
        else:
            status.add(" ")
        return status.to_rt() + output
