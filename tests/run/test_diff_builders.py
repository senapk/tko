from tko.enums.execution_result import ExecutionResult
from tko.run.diff_builder_down import DiffBuilderDown
from tko.run.diff_builder_side import DiffBuilderSide
from tko.run.unit import Unit
from tko.util.rt import RT
from tko.util.symbols import Symbols


def make_unit(
    expected: str,
    received: str,
    input_data: str = "",
    result: ExecutionResult = ExecutionResult.WRONG_OUTPUT,
) -> Unit:
    unit: Unit = Unit(case="sample", input_data=input_data, expected=expected)
    unit.set_received(received)
    unit.result = result
    return unit


def output_text(output: list[RT]) -> str:
    return "\n".join(line.plain() for line in output)


def test_diff_builder_down_renders_equal_output_without_mismatch_section() -> None:
    unit: Unit = make_unit("4\n", "4\n", "2\n", ExecutionResult.SUCCESS)

    output: str = output_text(DiffBuilderDown(60, unit).build_diff())

    assert "INSERIDO" in output
    assert "ESPERADO" in output
    assert "RECEBIDO" in output
    assert "4\n" in output
    assert "DESIGUAL" not in output
    assert output.splitlines()[-1].startswith("╰")


def test_diff_builder_down_renders_changed_and_extra_lines() -> None:
    unit: Unit = make_unit("alpha\nbeta\n", "alpha\ngamma\nextra\n", "go\n")

    output: str = output_text(DiffBuilderDown(60, unit).build_diff())

    assert "alpha\n" in output
    assert "beta↲" in output
    assert "gamma\n" in output
    assert "extra\n" in output
    assert "DESIGUAL" in output
    assert "(primeiro)" in output
    assert Symbols.arrow_up in output


def test_diff_builder_down_handles_output_when_expected_is_empty() -> None:
    unit: Unit = make_unit("", "unexpected\n")

    output: str = output_text(DiffBuilderDown(50, unit).build_diff())

    assert "RECEBIDO" in output
    assert "unexpected\n" in output
    assert "ESPERADO" not in output
    assert "DESIGUAL" not in output


def test_diff_builder_down_skips_empty_expected_section_when_input_exists() -> None:
    unit: Unit = make_unit("", "unexpected\n", "input\n")

    output: str = output_text(DiffBuilderDown(50, unit).build_diff())

    assert "INSERIDO" in output
    assert "RECEBIDO" in output
    assert "unexpected\n" in output
    assert "ESPERADO" not in output


def test_diff_builder_down_suppresses_first_difference_for_execution_errors() -> None:
    unit: Unit = make_unit(
        "expected\n", "actual\n", result=ExecutionResult.EXECUTION_ERROR
    )

    output: str = output_text(DiffBuilderDown(50, unit).build_diff())

    assert "ESPERADO" in output
    assert "RECEBIDO" in output
    assert "expected\n" in output
    assert "actual\n" in output
    assert "DESIGUAL" not in output
    assert "(primeiro)" not in output


def test_diff_builder_down_standalone_omits_input_and_inserts_unit_header() -> None:
    unit: Unit = make_unit("expected\n", "actual\n", "input\n")

    output: str = output_text(
        DiffBuilderDown(50, unit).standalone_diff().to_insert_header().build_diff()
    )

    assert "sample" in output
    assert "INSERIDO" not in output
    assert "input" not in output
    assert "ESPERADO" in output
    assert "RECEBIDO" in output


def test_diff_builder_down_tui_uses_bordered_content_lines() -> None:
    unit: Unit = make_unit("expected\n", "actual\n")

    output: str = output_text(DiffBuilderDown(50, unit).set_tui().build_diff())

    assert "ESPERADO" in output
    assert "RECEBIDO" in output
    assert any(line.endswith(Symbols.vbar) for line in output.splitlines())


def test_diff_builder_down_connects_input_header_to_existing_frame() -> None:
    unit: Unit = make_unit("expected\n", "actual\n", "input\n")

    output: list[str] = [
        line.plain()
        for line in DiffBuilderDown(50, unit).to_insert_header().build_diff()
    ]

    assert "sample" in output[1]
    assert "INSERIDO" in output[2]
    assert output[2].startswith("├")


def test_diff_builder_down_put_left_equal_handles_missing_rows() -> None:
    expected: RT = RT("expected")
    received: RT = RT("received")

    rows: list[tuple[RT, RT]] = DiffBuilderDown.put_left_equal(
        [(None, received), (expected, None)], None
    )

    assert rows[0][0].plain() == f"{Symbols.unequal} "
    assert rows[0][1].plain() == f"{Symbols.unequal} received"
    assert rows[1][0].plain() == f"{Symbols.unequal} expected"
    assert rows[1][1].plain() == f"{Symbols.unequal} "


def test_diff_builder_down_trims_missing_trailing_received_row() -> None:
    unit: Unit = make_unit("one\ntwo\n", "one\n")

    output: str = output_text(DiffBuilderDown(50, unit).build_diff())

    assert "two" in output
    assert "DESIGUAL" in output


def test_diff_builder_down_trims_missing_trailing_expected_row() -> None:
    unit: Unit = make_unit("one\n", "one\ntwo\n")

    lines: list[str] = output_text(DiffBuilderDown(50, unit).build_diff()).splitlines()
    expected_index: int = next(i for i, line in enumerate(lines) if "ESPERADO" in line)
    received_index: int = next(i for i, line in enumerate(lines) if "RECEBIDO" in line)
    expected_rows: list[str] = lines[expected_index + 1 : received_index]

    assert any("one" in line for line in expected_rows)
    assert not any(line.lstrip().startswith(Symbols.unequal) for line in expected_rows)
    assert "two" in "\n".join(lines[received_index + 1 :])


def test_diff_builder_side_renders_equal_output_with_equal_frame_bottom() -> None:
    unit: Unit = make_unit("same\n", "same\n", "input\n", ExecutionResult.SUCCESS)

    output: str = output_text(DiffBuilderSide(60, unit).build_diff())

    assert "INSERIDO" in output
    assert "ESPERADO" in output
    assert "RECEBIDO" in output
    assert "same" in output
    assert "DESIGUAL" not in output
    assert "┴" in output.splitlines()[-1]


def test_diff_builder_side_marks_changed_lines_and_first_mismatch() -> None:
    unit: Unit = make_unit("before\n", "after\n", "input\n")

    output: str = output_text(DiffBuilderSide(60, unit).build_diff())

    assert "before↲" in output
    assert "after↲" in output
    assert "DESIGUAL" in output
    assert "(primeiro)" in output
    assert Symbols.arrow_up in output


def test_diff_builder_side_standalone_header_omits_input_section() -> None:
    unit: Unit = make_unit("left\n", "right\n", "input\n")

    output: str = output_text(
        DiffBuilderSide(60, unit).standalone_diff().to_insert_header(True).build_diff()
    )

    assert "sample" in output
    assert "INSERIDO" not in output
    assert "input" not in output
    assert "ESPERADO" in output
    assert "RECEBIDO" in output
    assert "┬" in output


def test_diff_builder_side_connects_input_header_to_existing_frame() -> None:
    unit: Unit = make_unit("left\n", "right\n", "input\n")

    output: list[str] = [
        line.plain()
        for line in DiffBuilderSide(60, unit).to_insert_header(True).build_diff()
    ]

    assert "sample" in output[1]
    assert "INSERIDO" in output[2]
    assert "┬" in output[2]


def test_diff_builder_side_execution_error_uses_neutral_line_separator() -> None:
    unit: Unit = make_unit(
        "expected\n", "actual\n", result=ExecutionResult.COMPILATION_ERROR
    )

    output: str = output_text(DiffBuilderSide(60, unit).build_diff())

    assert "expected↲" in output
    assert "actual↲" in output
    assert "DESIGUAL" in output
    assert "(primeiro)" in output


def test_diff_builder_side_split_screen_handles_equal_missing_and_long_values() -> None:
    builder: DiffBuilderSide = DiffBuilderSide(24, make_unit("", ""))

    equal: RT = builder.split_screen(RT("same"), RT("same"))
    missing: RT = builder.split_screen(None, RT("right"))
    long_value: RT = builder.split_screen(RT("a very long left side"), RT("right"))

    assert Symbols.vbar in equal.plain()
    assert "right" in missing.plain()
    assert Symbols.vbar in missing.plain()
    assert len(long_value) <= 24


def test_diff_builder_side_titles_trim_to_narrow_terminal_width() -> None:
    builder: DiffBuilderSide = DiffBuilderSide(20, make_unit("", ""))

    title: RT = builder.title_side_by_side(
        RT("a very long expected label"), RT("a very long received label")
    )

    assert len(title) <= 20


def test_diff_builder_side_tui_flag_is_chainable() -> None:
    builder: DiffBuilderSide = DiffBuilderSide(40, make_unit("", ""))

    configured: DiffBuilderSide = builder.set_tui()

    assert configured is builder
    assert builder.tui is True
