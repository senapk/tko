from pathlib import Path

import pytest

from tko.game.source_xp_config import SourceXpConfig, XpExpressionError


@pytest.mark.parametrize(
    "content, reason",
    [
        ('---\nargs = [g, d, s]\nexpr = "g * d * s"\n---\n', "must be a mapping"),
        ("---\nargs: [g\n---\n", "invalid YAML"),
        ("---\nargs: [g]\n", "unclosed YAML"),
        ("---\nargs: [g]\n---\n", "must be declared together"),
    ],
)
def test_invalid_front_matter_explains_tag_syntax(content: str, reason: str) -> None:
    with pytest.raises(XpExpressionError) as caught:
        SourceXpConfig.from_markdown(content, "labs", Path("README.md"))

    message = str(caught.value)
    assert "labs:README.md" in message
    assert reason in message
    assert "':' instead of '='" in message
    assert '---\nargs: [g, l, s]\nexpr: "g * l * s"\n---' in message
    assert "`g=2 l=3 s=1 eval=diff`" in message


def test_suggested_front_matter_is_valid() -> None:
    config = SourceXpConfig.from_markdown(
        '---\nargs: [g, l, s]\nexpr: "g * l * s"\n---\n',
        "labs",
        Path("README.md"),
    )
    assert config.calculate({"g": 2.0, "l": 3.0, "s": 1.0}, "task", 6) == 6.0
