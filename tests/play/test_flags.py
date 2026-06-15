from tko.config.flags import BoolFlag, Flag, Flags, PanelMode, TaskGraphMode, ViewMode


class TestFlag:
    def test_toggle_cycles_values_and_invalid_value_falls_back_to_default(self):
        flag = Flag(
            id="mode",
            default_value="a",
            msgs={"a": "Alpha", "b": "Beta", "c": "Gamma"},
            description="toggle test",
        )

        flag.set_value("invalid")
        assert flag.get_value() == "a"

        flag.toggle()
        assert flag.get_value() == "b"

        flag.toggle()
        assert flag.get_value() == "c"

        flag.toggle()
        assert flag.get_value() == "a"


class TestBoolFlag:
    def test_true_false_helpers_and_invalid_assignment(self):
        flag = BoolFlag(
            id="show",
            default_value=True,
            msgs={True: "show", False: "hide"},
            description="bool flag",
        )

        assert flag.get_value() == BoolFlag.TRUE
        assert flag.is_true() is True

        flag.set_false()
        assert flag.get_value() == BoolFlag.FALSE
        assert flag.is_true() is False

        flag.set_value("unexpected")
        assert flag.get_value() == BoolFlag.TRUE


class TestFlags:
    def test_to_dict_exports_current_state(self):
        flags = Flags()
        flags.task_view_mode.set_view_all()
        flags.panel.set_logs()
        flags.task_graph_mode.set_time_view()
        flags.show_time.set_false()

        assert flags.to_dict() == {
            "inbox": ViewMode.ALL,
            "panel": PanelMode.LOGS,
            "task_graph_mode": TaskGraphMode.TIME,
            "show_time": BoolFlag.FALSE,
        }

    def test_from_dict_loads_values_and_uses_defaults_for_invalid_or_missing_entries(self):
        flags = Flags()
        flags.from_dict(
            {
                "inbox": ViewMode.ALL,
                "panel": "invalid-panel",
                "show_panel": BoolFlag.FALSE,
                "task_graph_mode": TaskGraphMode.TIME,
            }
        )

        assert flags.task_view_mode.is_all() is True
        assert flags.task_graph_mode.is_time_view() is True
        assert flags.show_time.is_true() is True

    def test_from_dict_round_trip_restores_all_flags(self):
        original = Flags()
        original.task_view_mode.set_view_all()
        original.panel.set_skills()
        original.task_graph_mode.set_time_view()
        original.show_time.set_false()

        restored = Flags()
        restored.from_dict(original.to_dict())

        assert restored.task_view_mode.is_all() is True
        assert restored.panel.is_skills() is True
        assert restored.task_graph_mode.is_time_view() is True
        assert restored.show_time.is_true() is False