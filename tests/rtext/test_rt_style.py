from tko.util.rt_style import RTStyle


def test_parse_plain_style():
    style = RTStyle.parse("")

    assert style.fg is None
    assert style.bg is None
    assert style.attrs == frozenset()
    assert style.is_plain()
    assert style.to_tag() == ""
    assert str(style) == ""


def test_parse_foreground_background_and_attrs():
    style = RTStyle.parse("rB_*/")

    assert style.fg == "r"
    assert style.bg == "B"
    assert style.attrs == frozenset({"_", "*", "/"})
    assert style.to_tag() == "rB*/_"
    assert not style.is_plain()


def test_parse_default_foreground_and_background_clear_to_plain():
    style = RTStyle.parse("dD")

    assert style.fg is None
    assert style.bg is None
    assert style.is_plain()


def test_parse_ignores_unknown_characters():
    style = RTStyle.parse("zr?Q")

    assert style == RTStyle.parse("r")


def test_overlay_replaces_colors_and_merges_attrs():
    base = RTStyle.parse("rB_")

    style = base.overlay(RTStyle.parse("gY*"))

    assert style.fg == "g"
    assert style.bg == "Y"
    assert style.attrs == frozenset({"_", "*"})


def test_overlay_accepts_style_tag_string():
    base = RTStyle.parse("r_")

    style = base.overlay("B/")

    assert style.fg == "r"
    assert style.bg == "B"
    assert style.attrs == frozenset({"_", "/"})


def test_clear_attrs_preserves_colors():
    style = RTStyle.parse("rB_*/").clear_attrs()

    assert style.fg == "r"
    assert style.bg == "B"
    assert style.attrs == frozenset()


def test_from_ansi_codes_reads_colors_and_attrs():
    style = RTStyle.from_ansi_codes(["31", "44", "1", "4", "3"])

    assert style == RTStyle.parse("rB*_/")


def test_from_ansi_codes_resets_base_style():
    base = RTStyle.parse("rB*_")

    style = RTStyle.from_ansi_codes(["0", "32"], base=base)

    assert style == RTStyle.parse("g")


def test_from_ansi_codes_overlays_base_style_without_reset():
    base = RTStyle.parse("rB_")

    style = RTStyle.from_ansi_codes(["33", "9"], base=base)

    assert style == RTStyle.parse("yB_!")


def test_ansi_returns_separate_escape_sequences_with_sorted_attrs():
    style = RTStyle.parse("rB_*/!")

    assert style.ansi() == "\033[31m\033[44m\033[9m\033[1m\033[3m\033[4m"


def test_plain_style_has_no_ansi_sequence():
    assert RTStyle.parse("").ansi() == ""
