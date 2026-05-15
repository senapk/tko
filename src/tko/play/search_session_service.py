from tko.play_tree.task_tree import TaskTree


class SearchSessionService:
    def __init__(self, tree: TaskTree):
        self.tree = tree
        self.repo = tree.repo
        self.backup_expanded: list[str] = []
        self.backup_selected: str = ""
        self.inbox_in_beggining: bool = False

    def start(self) -> None:
        self.backup_expanded = [value for value in self.tree.state.expanded]
        self.backup_selected = self.tree.state.selected
        self.tree.update(force_view_all=True)
        self.tree.expand_all()
        self.inbox_in_beggining = self.repo.flags.task_view_mode.is_inbox()
        self.repo.flags.task_view_mode.set_view_all()

    def cancel(self) -> None:
        self.tree.state.search = ""
        self.tree.state.expanded = {value for value in self.backup_expanded}
        self.tree.state.selected = self.backup_selected