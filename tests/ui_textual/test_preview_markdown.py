import pytest
from rich.console import Console
from rich.segment import Segment

from tko.ui_textual.preview_markdown import render_preview_markdown


@pytest.mark.parametrize("ending", ["---", "..."])
@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_yaml_front_matter_renders_as_highlighted_code(ending: str, newline: str) -> None:
    source: str = newline.join([
        "\ufeff---", "title: Task", "tags:", "  - loops", "description: |",
        "  Keep **literal** text and ``` fences", ending, "", "# Instructions",
    ])
    markdown = render_preview_markdown(source)
    console: Console = Console(width=90, force_terminal=True, color_system="truecolor")
    segments: list[Segment] = list(console.render(markdown))
    output: str = "".join(segment.text for segment in segments)
    assert "title: Task" in output
    assert "  - loops" in output
    assert "**literal**" in output
    assert "``` fences" in output
    assert "Instructions" in output
    assert any(segment.style is not None and segment.style.color is not None for segment in segments)
    assert markdown.markup.endswith("# Instructions")


@pytest.mark.parametrize("source", [
    "# Title\n\n---\n\nBody",
    "---\nUnclosed metadata",
    "```yaml\ntitle: Task\n```",
    "# Title\n\ntext\n---\n",
])
def test_ordinary_markdown_is_unchanged(source: str) -> None:
    assert render_preview_markdown(source).markup == source


def test_front_matter_without_body() -> None:
    assert render_preview_markdown("---\ntitle: Task\n---").markup == "```yaml\ntitle: Task\n```\n\n"
