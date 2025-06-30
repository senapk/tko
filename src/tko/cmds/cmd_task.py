from tko.settings.settings import Settings
from tko.settings.repository import Repository
from tko.play.task_graph import TaskGraph
from tko.util.raw_terminal import RawTerminal

class CmdTask:
    @staticmethod
    def show_graph(settings: Settings, rep: Repository, task_key: str, width: int | None = None, height: int | None = None):
        settings = settings
        rep = rep
        task_key = task_key
        if width is None:
            width = RawTerminal.get_terminal_size() // 2
        if height is None:
            height = round(width / 4)
        graph = TaskGraph(settings, rep, task_key, width, height).get_graph()
        for line in graph:
            print(line)