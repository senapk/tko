from tko.config.settings import Settings
from tko.repository.repository import Repository
from tko.play.task_graph import TaskGraph
from tko.util.raw_terminal import RawTerminal
from tko.util.console import Console
from tko.cmds.drafts_finder_cached import DraftsFinderCached
from tko.game.task import Task

class CmdTask:
    @staticmethod
    def find_task(rep: Repository, label: str) -> Task:
        task = rep.game.get_task(label)
        if task is not None:
            return task
        matches = [
            item for item in rep.game.tasks.values()
            if item.basic.key == label or item.basic.full_key.endswith(f"@{label}")
        ]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise ValueError(f"Task not found: {label}")
        raise ValueError(f"Task label is ambiguous: {label}")

    @staticmethod
    def show(settings: Settings, rep: Repository, label: str, width: int = 100, height: int = 12) -> None:
        task = CmdTask.find_task(rep, label)
        source = rep.sources.get(task.basic.source_name)
        target_file = rep.task_resolver.target_file(task)
        target_folder = rep.task_resolver.target_folder(task)
        downloaded = target_folder is not None and target_folder.exists()
        grader = task.grader

        Console.print(f"Task: {task.basic.full_key}")
        Console.print(f"Title: {task.basic.title}")
        Console.print(f"Source: {task.basic.source_name}")
        if source is not None:
            Console.print(f"Source URI: {source.path_or_url}")
            Console.print(f"Source editable: {'yes' if source.is_editable else 'no'}")
        Console.print(f"Evaluation: {task.config.eval.value}")
        Console.print(f"State: {CmdTask._state(task, downloaded)}")
        Console.print(
            f"Score: {grader.full_percent:.0f}%"
            f" | XP: {task.xp:g}"
            f" | Earned XP: {task.xp * grader.ratio:g}"
        )
        Console.print(f"Reachable: {'yes' if task.game.is_reachable else 'no'}")
        Console.print(f"Reference: {'yes' if task.is_reference else 'no'}")

        Console.print("Files:")
        if target_folder is None:
            Console.print("  target: none")
        else:
            Console.print(f"  folder: {target_folder}")
            Console.print(f"  README: {target_file} ({'present' if target_file and target_file.exists() else 'missing'})")
            for name in ("tests.toml", "tests.tio"):
                path = target_folder / name
                if path.exists():
                    Console.print(f"  tests: {path}")
            drafts = DraftsFinderCached(target_folder, rep.data.lang).load_source_files()
            for draft in drafts:
                Console.print(f"  draft: {draft}")

        graph = TaskGraph(settings, rep, task.basic.full_key, width, height)
        if not graph.eixo:
            Console.print("Graph: no history")
            return
        Console.print("Graph:")
        for line in graph.get_graph():
            Console.print(line)

    @staticmethod
    def _state(task: Task, downloaded: bool) -> str:
        if task.location.is_external and not downloaded:
            return "not downloaded"
        if task.grader.is_complete:
            return "complete"
        if task.grader.in_progress:
            return "in progress"
        return "not started"

    @staticmethod
    def show_graph(settings: Settings, rep: Repository, task_key: str, width: int | None = None, height: int | None = None):
        settings = settings
        rep = rep
        task_key = task_key
        if width is None:
            width = RawTerminal.get_terminal_size() // 2
        if height is None:
            height = round(width / 4)
        graph = TaskGraph(settings, rep, task_key, width, height).get_output()
        for line in graph:
            Console.print(line)
