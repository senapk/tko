from pathlib import Path

from tko.game.task_enums import TaskType
from tko.game.task_location import TaskLocation


def test_clone_preserves_fields_for_local_editable_resource(tmp_path: Path) -> None:
    location = TaskLocation()
    location.raw_link = "task.md"
    location.line_number = 7
    location.line_data = "- [ ] [@task title](task.md)"
    location.task_type = TaskType.MAKE
    location.remote_dir = (tmp_path / "repo").resolve()
    location.relative_path = Path("task")
    location.remote_import = True

    clone = location.clone()

    assert clone.raw_link == "task.md"
    assert clone.line_number == 7
    assert clone.line_data == "- [ ] [@task title](task.md)"
    assert clone.task_type == TaskType.MAKE
    assert clone.remote_dir == (tmp_path / "repo").resolve()
    assert clone.relative_path == Path("task")
    assert clone.remote_import is True


def test_clone_preserves_fields_for_external_view_resource() -> None:
    location = TaskLocation()
    location.task_type = TaskType.READ
    location.external_url = "https://example.com/material"

    clone = location.clone()

    assert clone.task_type == TaskType.READ
    assert clone.external_url == "https://example.com/material"
    assert clone.is_read is True
    assert clone.is_read_http_link is True
