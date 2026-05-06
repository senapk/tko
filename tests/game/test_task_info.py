from tko.game.task_info import TaskSelfInfo


class TestTaskInfo:
    def test_load_from_kv_and_get_kv_round_trip(self):
        kv = {
            TaskSelfInfo.Keys.rate_str: "75",
            TaskSelfInfo.Keys.study_str: "45",
            TaskSelfInfo.Keys.friend_str: "monitor",
            TaskSelfInfo.Keys.feedback_str: "1",
            TaskSelfInfo.Keys.guided_str: "1",
            TaskSelfInfo.Keys.ia_concept_str: "1",
            TaskSelfInfo.Keys.ia_problem_str: "1",
            TaskSelfInfo.Keys.ia_coding_str: "1",
            TaskSelfInfo.Keys.ia_debug_str: "1",
            TaskSelfInfo.Keys.ia_refactor_str: "1",
        }

        info = TaskSelfInfo().load_from_kv(kv)

        assert info.rate == 75
        assert info.study == 45
        assert info.friend == "monitor"
        assert info.feedback is True
        assert info.guided is True
        assert info.ia_concept is True
        assert info.ia_problem is True
        assert info.ia_code is True
        assert info.ia_debug is True
        assert info.ia_refactor is True
        assert info.get_kv() == kv

    def test_setters_keep_previous_value_for_negative_or_out_of_range_numbers(self):
        info = TaskSelfInfo()

        info.set_study("15")
        info.set_study("-3")
        assert info.study == 15

        info.set_rate("80")
        info.set_rate("101")
        assert info.rate == 80

    def test_setters_reset_to_zero_for_non_numeric_values(self):
        info = TaskSelfInfo()

        info.set_study("12")
        info.set_study("abc")
        assert info.study == 0

        info.set_rate("60")
        info.set_rate("abc")
        assert info.rate == 0

    def test_copy_quality_from_and_clone(self):
        source = TaskSelfInfo().load_from_kv(
            {
                TaskSelfInfo.Keys.rate_str: "90",
                TaskSelfInfo.Keys.study_str: "30",
                TaskSelfInfo.Keys.friend_str: "dupla",
                TaskSelfInfo.Keys.feedback_str: "1",
                TaskSelfInfo.Keys.guided_str: "1",
                TaskSelfInfo.Keys.ia_concept_str: "1",
                TaskSelfInfo.Keys.ia_problem_str: "1",
                TaskSelfInfo.Keys.ia_coding_str: "1",
                TaskSelfInfo.Keys.ia_debug_str: "1",
                TaskSelfInfo.Keys.ia_refactor_str: "1",
            }
        )
        target = TaskSelfInfo().load_from_kv(
            {
                TaskSelfInfo.Keys.rate_str: "20",
                TaskSelfInfo.Keys.study_str: "5",
            }
        )

        target.copy_quality_from(source)

        assert target.rate == 20
        assert target.study == 5
        assert target.friend == "dupla"
        assert target.feedback is True
        assert target.guided is True
        assert target.ia_concept is True
        assert target.ia_problem is True
        assert target.ia_code is True
        assert target.ia_debug is True
        assert target.ia_refactor is True

        clone = source.clone()
        clone.friend = "outra pessoa"

        assert clone.get_kv() == source.get_kv() | {TaskSelfInfo.Keys.friend_str: "outra pessoa"}
        assert source.friend == "dupla"