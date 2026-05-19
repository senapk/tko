import pytest

from tko.util.rt import RT, ParseError


def test_inline_style_and_reset():
    t = RT.parse("[r]hello[.] world")
    assert t.plain() == "hello world"
    assert t.runs == (("r", "hello"), ("", " world"))


def test_content_positional():
    t = RT.parse("hello <$>", "world")
    assert t.runs == (("", "hello world"),)


def test_content_named():
    t = RT.parse("hello <$name>", name="world")
    assert t.runs == (("", "hello world"),)


def test_content_positional_with_inline_style():
    t = RT.parse("hello <$:r>", "world")
    assert t.runs == (("", "hello "), ("r", "world"))


def test_content_named_with_inline_style():
    t = RT.parse("hello <$name:r>", name="world")
    assert t.runs == (("", "hello "), ("r", "world"))


def test_content_named_rt_with_inline_style_overlay():
    t = RT.parse("[$cor]hello <$name:B>", cor="r", name=RT("file", "Y"))
    assert t.runs == (("r", "hello "), ("rB", "file"))


def test_content_rt_overlay_current_style():
    t = RT.parse("[$cor]hello <$name>", cor="r", name=RT("file", "Y"))
    assert t.runs == (("r", "hello "), ("rY", "file"))


def test_content_tuple_overlay_current_style():
    t = RT.parse("[$cor]<$>", ("Y", "ok"), cor="r")
    assert t.runs == (("rY", "ok"),)


def test_style_positional_and_named_overlay():
    t = RT.parse("[$]abc[$fundo]def", "r", fundo="Y")
    assert t.runs == (("r", "abc"), ("rY", "def"))


def test_named_style_with_reset():
    t = RT.parse("[$base]abc[.fundo]def", base="r", fundo="Y")
    assert t.runs == (("r", "abc"), ("Y", "def"))


def test_positional_consumption_order_for_style_and_content():
    t = RT.parse("[$]<$>", "r", "ok")
    assert t.runs == (("r", "ok"),)


def test_escapes_for_all_delimiters():
    t = RT.parse("[[ ]] << >>")
    assert t.plain() == "[ ] < >"


def test_error_missing_positional_content():
    with pytest.raises(ParseError, match=r"missing positional value for <\$>"):
        RT.parse("x<$>")


def test_error_missing_named_content():
    with pytest.raises(ParseError, match="missing named value: nome"):
        RT.parse("<$nome>")


def test_malformed_style_after_colon_is_ignored_for_value_placeholder():
    t = RT.parse("x<$:>", "ok")
    assert t.runs == (("", "xok"),)


def test_error_missing_positional_style():
    with pytest.raises(ParseError, match=r"missing positional style for \[\$\]"):
        RT.parse("[$]x")


def test_error_missing_named_style():
    with pytest.raises(ParseError, match="missing named style: cor"):
        RT.parse("[$cor]x")


def test_error_missing_closing_bracket():
    with pytest.raises(ParseError, match=r"missing closing \]"):
        RT.parse("[r")


def test_error_missing_closing_angle():
    with pytest.raises(ParseError, match="missing closing >"):
        RT.parse("<$nome")


def test_paren_is_literal_text():
    t = RT.parse("(cor")
    assert t.plain() == "(cor"
