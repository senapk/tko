from pathlib import Path

from tko.game.task_resource import TaskResource, ResourceType


def test_clone_preserves_fields_for_local_editable_resource(tmp_path: Path) -> None:
    location = TaskResource()
    location.raw_link = "task.md"
    location.line_number = 7
    location.line_data = "- [ ] [@task title](task.md)"
    location.resource_type = ResourceType.DO
    location.remote_dir = (tmp_path / "repo").resolve()
    location.relative_path = Path("task")
    location.editable_source = True

    clone = location.clone()

    assert clone.raw_link == "task.md"
    assert clone.line_number == 7
    assert clone.line_data == "- [ ] [@task title](task.md)"
    assert clone.resource_type == ResourceType.DO
    assert clone.remote_dir == (tmp_path / "repo").resolve()
    assert clone.relative_path == Path("task")
    assert clone.editable_source is True


def test_clone_preserves_fields_for_external_view_resource() -> None:
    location = TaskResource()
    location.resource_type = ResourceType.READ
    location.external_url = "https://example.com/material"

    clone = location.clone()

    assert clone.resource_type == ResourceType.READ
    assert clone.external_url == "https://example.com/material"
    assert clone.is_read is True
    assert clone.is_link is True
