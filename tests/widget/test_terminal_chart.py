from tko.widget.terminal_chart import Series, TerminalChart


def test_chart_renders_labelled_axes_with_ticks_without_ansi():
    chart = TerminalChart(8, 4, [Series([(0, 0), (1, 100)], "g")], y_max=100)

    lines = chart.render()

    assert len(lines) == 4
    assert [len(line) for line in lines] == [8, 8, 8, 8]
    assert all("\033" not in line.plain() for line in lines)
    image = "\n".join(line.plain() for line in lines)
    assert "▓" in image
    assert "100┤" in image
    assert "0┼" in image
    assert "┬" in image
    assert "0" in lines[-1].plain()


def test_marker_series_is_rendered_over_line_series():
    chart = TerminalChart(
        7,
        3,
        [Series([(0, 50), (1, 50)], "g"), Series([(0, 50)], "r", line=False)],
        y_max=100,
    )

    marker = next(
        (style, text)
        for line in chart.render()
        for style, text in line.runs
        if "█" in text
    )

    assert marker[1] == "█"
    assert str(marker[0]) == "r"


def test_chart_does_not_expand_a_narrow_panel():
    chart = TerminalChart(5, 3, [Series([(0, 0), (1, 100)], "g")], y_max=100)

    lines = chart.render()

    assert [len(line) for line in lines] == [5, 5, 5]
