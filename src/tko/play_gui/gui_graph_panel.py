from tko.collect.task_user_data import TaskUserData
from tko.config.settings import Settings
from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.tree_item import IsTreeItem
from tko.play.daily_graph import DailyGraph
from tko.config.flags import Flags
from tko.widget.frame import Frame
from tko.play.images import opening
from tko.play.task_graph import TaskGraph
from tko.repository.repository import Repository
from tko.util.rt import RT


class GuiGraphPanel:

    def __init__(self, settings: Settings, repo: Repository, flags: Flags):
        self.settings = settings
        self.repo = repo
        self.flags = flags
        self.xray_offset: int = 0

    def get_task_graph(self, task_key: str, width: int, height: int) -> tuple[bool, list[RT], list[RT]]:
        tg = TaskGraph(self.settings, self.repo, task_key, width, height)
        header, graph = tg.get_output()
        if len(graph) == 0:
            return False, [], []
        return True, header, graph
    
    def get_history(self) -> tuple[bool, list[RT], list[RT]]:
        history: list[TaskUserData] = self.repo.logger.tasks.mount_task_history(self.repo.game)
        header = [RT.parse(" [r]History ")]
        task_pad = max((len(item.key) for item in history), default=0) + 2
        quest_pad = max((len(item.quest) for item in history), default=0) + 2
        list_data: list[RT] = []            
        for item in history:
            item.resume.events = 0 # hide events for history
            text = (str(item.get_kv(include_key=False, include_quest=False))
                    .replace("'", "").replace("{", "").replace("}", "")
                    .replace("grader: ", "").replace(", init: ", "%, ").replace("duration: ", "").replace("executions: ", "exec: "))
            list_data.append(RT.parse(f"[g]{item.key:<{task_pad}}[.] {item.quest:<{quest_pad}} {text}"))
        return True, header, list_data


    def get_daily_graph(self, width: int, height: int) -> tuple[bool, list[RT], list[RT]]:
        header, graph = DailyGraph(self.repo.logger, width, height).get_graph()
        if len(graph) == 0:
            return False, [], []
        return True, header, graph

    def show(self, frame: Frame, selected: IsTreeItem | None) -> None:
        lines, cols = frame.get_inner()
        made = False
        list_data: list[RT] = []
        width = cols - 2
        if width < 5:
            width = 5
        header: list[RT] = []
        if self.flags.panel.is_graph() or self.flags.panel.is_logs():
            height = lines - 2
            if height < 3:
                height = 3
            if isinstance(selected, Task):
                made, header, list_data = self.get_task_graph(selected.basic.full_key, width, height)
            elif isinstance(selected, Quest):
                if self.flags.panel.is_graph():
                    made, header, list_data = self.get_daily_graph(width, height)
                elif self.flags.panel.is_logs():
                    made, header, list_data = self.get_history()
        if not made:
            list_data = [RT(x).rjust(width) for x in opening["parrot"].splitlines()]

        if self.xray_offset < 0:
            self.xray_offset = 0
        if self.xray_offset >= len(list_data) - lines + 2:
            self.xray_offset = len(list_data) - lines + 2

        offset = 0
        if self.flags.panel.is_logs():
            offset = self.xray_offset

        dy, _ = frame.get_inner()
        if self.flags.panel.is_logs():
            if header:
                frame.set_header(RT(" Scroll Up[PageUp]  ScrollDown[PgDown] "), "^")
                frame.set_footer(header[0], "^")
            frame.set_scrollbar(offset, len(list_data), "right")
            count = -1
            line_count = 0
            for line in list_data:
                count += 1
                if count < offset:
                    continue
                if line_count > dy - 1:
                    break
                frame.write(line_count, 0, line)
                line_count += 1
        else:
            if self.flags.panel.is_graph() and isinstance(selected, Task):
                exec_color = "X" if self.flags.task_graph_mode.is_executions() else "."
                time_color = "X" if self.flags.task_graph_mode.is_time_view() else "."
                frame.set_header(RT.parse(f" [{exec_color}]EXEC[[PageUp]][]  [{time_color}]TIME[[PgDown]][] "), "^")
            if header:
                frame.set_footer(header[0], "^")
            count = -1
            line_count = 0
            for line in list_data:
                count += 1
                if count < offset:
                    continue
                frame.write(line_count, 0, line)
                line_count += 1

        frame.draw()
