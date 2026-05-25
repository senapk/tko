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