from pathlib import Path

from tko.game.task import Task
from tko.game.task_location import TaskLocation
from tko.game.task_resolver import TaskResolver
from tko.play.preview_service import PreviewService
from tko.repository.git_cache import GitCache
from tko.util.git_hub_url import GitHubUrl
from tko.config.flags import Flags, PanelMode


class SourceResolver:
    def __init__(self, path: Path | None) -> None:
        self.path: Path | None = path
        self.calls: list[bool] = []

    def origin_file(self, task: Task, load_git: bool) -> Path | None:
        self.calls.append(load_git)
        return self.path


def test_original_source_without_materialization(tmp_path: Path) -> None:
    source: Path = tmp_path / "source" / "README.md"
    source.parent.mkdir()
    source.write_text("# Original", encoding="utf-8")
    task: Task = Task()
    task.basic.source_name = "course"
    task.basic.key = "activity"
    task.location = TaskLocation(index_path=source, raw_link="README.md", external_source=True)
    resolver: TaskResolver = TaskResolver(GitCache(tmp_path / "cache"), tmp_path)
    preview: PreviewService = PreviewService(resolver)
    assert preview.load(task).markdown == "# Original"
    target: Path = tmp_path / "course" / "labs" / "activity" / "README.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Modified working copy", encoding="utf-8")
    assert preview.load(task).markdown == "# Original"
    source.write_text("# Updated original", encoding="utf-8")
    assert preview.load(task).markdown == "# Updated original"


def test_placeholder_and_file_failures(tmp_path: Path) -> None:
    path: Path = tmp_path / "README.md"
    resolver: SourceResolver = SourceResolver(path)
    preview: PreviewService = PreviewService(resolver)
    task: Task = Task()
    assert preview.load(None).status == "select"
    assert resolver.calls == []
    assert preview.load(task).status == "unavailable"
    path.write_text(" \n", encoding="utf-8")
    assert preview.load(task).status == "empty"
    path.write_bytes(b"\xff")
    assert preview.load(task).status == "unreadable"
    resolver.path = tmp_path  # A directory cannot be read as a README.
    assert preview.load(task).status == "unreadable"
    resolver.path = None
    assert preview.load(task).status == "unavailable"
    assert resolver.calls == [False] * 5


def test_git_cache_only(tmp_path: Path) -> None:
    cache: GitCache = GitCache(tmp_path / "cache")
    url: GitHubUrl | None = GitHubUrl.parse("https://github.com/example/course/blob/main/labs/task/README.md")
    assert url is not None
    task: Task = Task()
    task.location = TaskLocation(git_hub_url=url)
    preview: PreviewService = PreviewService(TaskResolver(cache, tmp_path))
    assert preview.load(task).status == "unavailable"
    assert not cache.cache_dir.exists()
    path, _ = cache.git_hub_url_to_path(url, load_git=False)
    path.parent.mkdir(parents=True)
    path.write_text("# Cached original", encoding="utf-8")
    assert preview.load(task).markdown == "# Cached original"
    assert cache.updated == {}


def test_preview_flag_roundtrip_and_cycle() -> None:
    flags: Flags = Flags()
    assert flags.panel.is_skills()
    flags.panel.toggle()
    assert flags.panel.is_preview()
    restored: Flags = Flags()
    restored.from_dict(flags.to_dict())
    assert restored.panel.is_preview()
    restored.panel.toggle()
    assert restored.panel.is_graph()
    restored.panel.set_preview()
    assert restored.panel.get_value() == PanelMode.PREVIEW
