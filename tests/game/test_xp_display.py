from tko.game.xp_display import format_task_xp, truncate_total_xp


def test_task_xp_is_truncated_and_shown_with_one_decimal() -> None:
    assert format_task_xp(1.59) == "1.5"
    assert format_task_xp(1.0) == "1.0"


def test_task_xp_is_truncated_to_an_integer_from_ten() -> None:
    assert format_task_xp(10.9) == "10"
    assert format_task_xp(99.9) == "99"


def test_total_xp_hides_fraction_without_rounding() -> None:
    assert truncate_total_xp(9.9) == 9
