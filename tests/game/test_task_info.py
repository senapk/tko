from tko.game.task_info import TaskSelfInfo


class TestTaskInfo:
    def test_load_from_kv_and_get_kv_round_trip(self):
        kv = {
            TaskSelfInfo.Key.RATE: "75",
            TaskSelfInfo.Key.STUDY_TIME: "45",
            TaskSelfInfo.Key.FRIEND: "monitor",
            TaskSelfInfo.Key.FEEDBACK: "1",
            TaskSelfInfo.Key.GUIDED: "1",
            TaskSelfInfo.Key.IA_CONCEPT: "1",
            TaskSelfInfo.Key.IA_PROBLEM: "1",
            TaskSelfInfo.Key.IA_CODING: "1",
            TaskSelfInfo.Key.IA_DEBUG: "1",
            TaskSelfInfo.Key.IA_REFACTOR: "1",
        }

        info = TaskSelfInfo().from_kv(kv)

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
        source = TaskSelfInfo().from_kv(
            {
                TaskSelfInfo.Key.RATE: "90",
                TaskSelfInfo.Key.STUDY_TIME: "30",
                TaskSelfInfo.Key.FRIEND: "dupla",
                TaskSelfInfo.Key.FEEDBACK: "1",
                TaskSelfInfo.Key.GUIDED: "1",
                TaskSelfInfo.Key.IA_CONCEPT: "1",
                TaskSelfInfo.Key.IA_PROBLEM: "1",
                TaskSelfInfo.Key.IA_CODING: "1",
                TaskSelfInfo.Key.IA_DEBUG: "1",
                TaskSelfInfo.Key.IA_REFACTOR: "1",
            }
        )
        target = TaskSelfInfo().from_kv(
            {
                TaskSelfInfo.Key.RATE: "20",
                TaskSelfInfo.Key.STUDY_TIME: "5",
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

        assert clone.get_kv() == source.get_kv() | {TaskSelfInfo.Key.FRIEND: "outra pessoa"}
        assert source.friend == "dupla"