from pathlib import Path

import pytest

from tko.game.source_xp_config import SourceXpConfig
from tko.game.task_enums import EvalMode
from tko.game.task_matcher import TaskMatcher


def config() -> SourceXpConfig:
    return SourceXpConfig.from_markdown(
        '---\nvar: [value, depth]\nxp: "value * depth"\n---\n', "course", Path("README.md")
    )


class TestTaskMatcher:
    def test_extracts_declared_numeric_variables(self) -> None:
        matcher = TaskMatcher(config())
        assert matcher.match_pattern("- [ ] `@task value=3 depth=2 eval=self` [Title](task/README.md)")
        assert matcher.key == "task"
        assert matcher.eval == EvalMode.SELF
        assert matcher.variables == {"value": 3.0, "depth": 2.0}
        assert matcher.get_filled_fields() == ["@task", "eval=self", "value=3", "depth=2"]

    def test_rejects_undeclared_variable(self) -> None:
        with pytest.raises(ValueError, match="Undeclared task variable: scope"):
            TaskMatcher(config()).match_pattern("- [ ] `@task value=3 depth=2 scope=1 eval=diff` [Title](task/README.md)")

    def test_rejects_non_numeric_variable(self) -> None:
        with pytest.raises(ValueError, match="integer or real"):
            TaskMatcher(config()).match_pattern("- [ ] `@task value=many depth=2 eval=diff` [Title](task/README.md)")

    def test_source_without_configuration_preserves_annotations(self) -> None:
        matcher = TaskMatcher()
        assert matcher.match_pattern("- [ ] `@task gain=3 gcs=312 eval=diff` [Title](task/README.md)")
        assert matcher.variables == {}
        assert matcher.get_filled_fields() == ["@task", "eval=diff", "gain=3", "gcs=312"]

    def test_requires_evaluation_mode(self) -> None:
        with pytest.raises(ValueError, match="Task evaluation is required"):
            TaskMatcher(config()).match_pattern("- [ ] `@task value=2 depth=1` [Title](task/README.md)")
