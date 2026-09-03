import pytest

from tko.game.task_enums import EvalMode
from tko.game.task_matcher import TaskMatcher


class TestTaskMatcher:
    def test_match_full_pattern_extracts_groups(self):
        matcher = TaskMatcher()
        assert matcher.match_pattern("- [ ] `@chave eval=diff` [Minha tarefa](path/to/task.md)  #obs")
        assert matcher.key == "chave"
        assert matcher.title == "Minha tarefa"
        assert matcher.link == "path/to/task.md"

    def test_match_full_pattern_accepts_checked_and_unchecked(self):
        assert TaskMatcher().match_pattern("- [x] `eval=none` [Tarefa](task.md)")
        assert TaskMatcher().match_pattern("- [ ] `eval=none` [Tarefa](task.md)")

    def test_invalid_line_does_not_overwrite_previous_state(self):
        matcher = TaskMatcher()
        assert matcher.match_pattern("- [ ] @k eval=diff [Titulo](task.md) after")
        assert not matcher.match_pattern("linha sem formato")
        assert matcher.key == "k"
        assert matcher.title == "Titulo"

    def test_parses_and_renders_canonical_fields(self):
        matcher = TaskMatcher()
        assert matcher.match_pattern("- [ ] `@foo gain=3 cost=2 size=3 eval=self` [Titulo](task/README.md)")
        assert matcher.key == "foo"
        assert matcher.gain == 3
        assert matcher.cost == 2
        assert matcher.size == 3
        assert matcher.eval == EvalMode.SELF
        assert matcher.get_filled_fields() == ["@foo", "eval=self", "gcs=323"]

    def test_none_defaults_and_filled_fields(self):
        matcher = TaskMatcher()
        assert matcher.match_pattern("- [ ] `@reading eval=none` [Material](wiki/git/README.md)")
        assert matcher.eval == EvalMode.NONE
        assert matcher.get_filled_fields() == ["@reading", "eval=none", "gcs=1"]

    @pytest.mark.parametrize(
        ("gcs", "expected"),
        [("1", (1, 1, 1)), ("3", (3, 1, 1)), ("32", (3, 2, 1)), ("312", (3, 1, 2))],
    )
    def test_parses_compact_gcs_fields(self, gcs: str, expected: tuple[int, int, int]):
        matcher = TaskMatcher()
        assert matcher.match_pattern(f"- [ ] `@task eval=diff gcs={gcs}` [Titulo](task/README.md)")
        assert (matcher.gain, matcher.cost, matcher.size) == expected

    @pytest.mark.parametrize(
        ("fields", "expected"),
        [
            ("gcs=312 gain=2", (2, 1, 2)),
            ("gain=2 gcs=312", (2, 1, 2)),
            ("gcs=312 cost=6", (3, 6, 2)),
            ("cost=6 gcs=312", (3, 6, 2)),
            ("gcs=312 size=3", (3, 1, 3)),
            ("size=3 gcs=312", (3, 1, 3)),
            ("gcs=312 gain=2 cost=6 size=3", (2, 6, 3)),
            ("gain=2 cost=6 size=3 gcs=312", (2, 6, 3)),
        ],
    )
    def test_explicit_fields_override_gcs_regardless_of_order(self, fields: str, expected: tuple[int, int, int]):
        matcher = TaskMatcher()
        assert matcher.match_pattern(f"- [ ] `@task eval=diff {fields}` [Titulo](task/README.md)")
        assert (matcher.gain, matcher.cost, matcher.size) == expected

    @pytest.mark.parametrize("gcs", ["", "0", "10", "1234", "4", "37", "314"])
    def test_rejects_invalid_gcs_fields(self, gcs: str):
        with pytest.raises(ValueError, match="gcs="):
            TaskMatcher().match_pattern(f"- [ ] `@task eval=diff gcs={gcs}` [Titulo](task/README.md)")

    @pytest.mark.parametrize(
        ("indicators", "gcs"),
        [((1, 1, 1), "1"), ((3, 1, 1), "3"), ((3, 2, 1), "32"), ((3, 1, 2), "312")],
    )
    def test_renders_gcs_without_trailing_default_values(self, indicators: tuple[int, int, int], gcs: str):
        matcher = TaskMatcher()
        matcher.gain, matcher.cost, matcher.size = indicators
        assert matcher.get_filled_fields() == ["gcs=" + gcs]

    def test_caps_game_indicators_at_their_supported_ranges(self):
        matcher = TaskMatcher()
        assert matcher.match_pattern("- [ ] `@limits gain=9 cost=9 size=9 eval=diff` [Titulo](task/README.md)")
        assert (matcher.gain, matcher.cost, matcher.size) == (3, 6, 3)

    @pytest.mark.parametrize(
        "field",
        ["hard=2", "tier=2", "xp=2", "type=wiki", "type=self", "type=diff", "type=code", "eval=test"],
    )
    def test_rejects_removed_fields(self, field: str):
        with pytest.raises(ValueError):
            TaskMatcher().match_pattern(f"- [ ] `@task {field}` [Titulo](task/README.md)")

    def test_requires_evaluation_mode(self):
        with pytest.raises(ValueError, match="Task evaluation is required"):
            TaskMatcher().match_pattern("- [ ] `@task gain=2` [Titulo](task/README.md)")
