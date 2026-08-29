from tko.game.task_matcher import TaskMatcher


class TestTaskMatcher:
    def test_match_full_pattern_extracts_groups(self):
        matcher = TaskMatcher()

        line = "- [ ]   @chave :test [Minha tarefa](path/to/task.md)  #obs"
        found = matcher.match_pattern(line)

        assert found is True
        assert matcher.raw_pre == "   @chave :test "
        assert matcher.title == "Minha tarefa"
        assert matcher.link == "path/to/task.md"
        assert matcher.raw_pos == "  #obs"

    def test_match_full_pattern_filters_backticks_and_html_comment_tags(self):
        matcher = TaskMatcher()

        line = "- [ ] `@key` <!--main:10--> [Titulo](task.md)"
        found = matcher.match_pattern(line)

        assert found is True
        raw_middle = matcher.filter_tags(" `@key` <!--main:10--> ")
        assert "`" not in raw_middle
        assert "<!--" not in raw_middle
        assert "-->" not in raw_middle
        assert "@key" in raw_middle
        assert "main:10" in raw_middle

    def test_match_full_pattern_accepts_checked_and_unchecked(self):
        matcher = TaskMatcher()

        # Deve aceitar tanto marcada quanto desmarcada
        found_checked = matcher.match_pattern("- [x] [Tarefa](task.md)")
        found_unchecked = matcher.match_pattern("- [ ] [Tarefa](task.md)")

        assert found_checked is True
        assert found_unchecked is True

    def test_match_full_pattern_invalid_line_does_not_overwrite_previous_state(self):
        matcher = TaskMatcher()

        assert matcher.match_pattern("- [ ] @k [  Titulo ](task.md) after") is True

        found = matcher.match_pattern("linha sem formato")

        assert found is False
        assert matcher.raw_pre == " @k "
        assert matcher.title == "  Titulo "
        assert matcher.link == "task.md"
        assert matcher.raw_pos == " after"

    def test_match_pattern_with_gain_hard_size_eval_type(self):
        matcher = TaskMatcher()
        line = "- [ ] `@foo gain=3 hard=2 size=4 type=make eval=self` [Titulo](task/README.md)"
        assert matcher.match_pattern(line) is True
        assert matcher.key == "foo"
        assert matcher.gain == 3
        assert matcher.hard == 2
        assert matcher.size == 4
        assert matcher.is_make is True
        assert matcher.eval.value == "self"
        assert matcher.get_filled_fields() == ["@foo", "gain=3", "hard=2", "size=4", "type=make", "eval=self"]

    def test_match_pattern_with_legacy_xp_tier(self):
        matcher = TaskMatcher()
        line = "- [ ] `@bar xp=5 tier=3` [Titulo](task/README.md)"
        assert matcher.match_pattern(line) is True
        assert matcher.key == "bar"
        assert matcher.gain == 5
        assert matcher.hard == 3
        assert matcher.size == 1
        assert matcher.is_make is True
        assert matcher.eval.value == "test"
        assert matcher.get_filled_fields() == ["@bar", "gain=5", "hard=3", "size=1", "type=make", "eval=test"]

    def test_read_task_defaults_and_filled_fields(self):
        matcher = TaskMatcher()
        line = "- [ ] `@read_task type=read` [Material](wiki/git/README.md)"
        assert matcher.match_pattern(line) is True
        assert matcher.key == "read_task"
        assert matcher.is_read is True
        assert matcher.eval.value == "self"
        assert matcher.get_filled_fields() == ["@read_task", "gain=1", "type=read", "eval=self"]