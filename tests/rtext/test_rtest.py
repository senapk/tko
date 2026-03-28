from tko.util.rtext import RText, RBuffer


# =========================================================
# PARSE
# =========================================================

def test_parse_plain():
    t = RText.parse("hello")
    assert t.plain() == "hello"
    assert t.runs == (("", "hello"),)


def test_parse_style():
    t = RText.parse("{r}hello")
    assert t.runs == (("r", "hello"),)


def test_parse_reset():
    t = RText.parse("{r}hello{.} world")
    assert t.runs == (("r", "hello"), ("", " world"))


def test_parse_overlay():
    t = RText.parse("{r}red {B}blue")
    # overlay -> rB
    assert t.runs == (("r", "red "), ("rB", "blue"))


def test_parse_reset_overlay():
    t = RText.parse("{r}red {.B}blue")
    assert t.runs == (("r", "red "), ("B", "blue"))


def test_parse_argument_string():
    t = RText.parse("Hello {}", "World")
    assert t.runs == (("", "Hello World"),)


def test_parse_argument_text_overlay():
    name = RText("World", "y")
    t = RText.parse("{r}Hello {}", name)
    assert t.runs == (("r", "Hello "), ("y", "World"))


def test_parse_escape():
    t = RText.parse("{{ hello }}")
    assert t.plain() == "{ hello }"


def test_parse_multiple_args():
    t = RText.parse("{} + {} = {}", 1, 2, 3)
    assert t.plain() == "1 + 2 = 3"


# =========================================================
# TEXT BASIC
# =========================================================

def test_concat():
    t = RText("A", "r") + RText("B", "g")
    assert t.plain() == "AB"
    assert len(t.runs) == 2


def test_merge_runs():
    t = RText("A", "r") + RText("B", "r")
    assert len(t.runs) == 1
    assert t.runs[0] == ("r", "AB")


def test_len():
    t = RText("hello", "r")
    assert len(t) == 5


def test_plain():
    t = RText.parse("{r}hello{.} world")
    assert t.plain() == "hello world"


# =========================================================
# STRING METHODS
# =========================================================

def test_upper():
    t = RText("hello", "r").upper()
    assert t.runs == (("r", "HELLO"),)


def test_lower():
    t = RText("HELLO", "r").lower()
    assert t.runs == (("r", "hello"),)


def test_replace_simple():
    t = RText.parse("hello world")
    t2 = t.replace("world", "there", "r")
    assert t2.plain() == "hello there"


def test_replace_across_runs():
    t = RText.from_runs([
        ("r", "Hel"),
        ("g", "lo Wo"),
        ("y", "rld"),
    ])
    t2 = t.replace("lo Wo", "X", "b")
    assert t2.plain() == "HelXrld"


# =========================================================
# SPLIT
# =========================================================

def test_split_preserve_style():
    t = RText.from_runs([
        ("r", "Hello"),
        ("", " "),
        ("g", "World"),
    ])
    parts = t.split(" ")
    assert parts[0].runs == (("r", "Hello"),)
    assert parts[1].runs == (("g", "World"),)


# =========================================================
# ALIGN
# =========================================================

def test_ljust():
    t = RText("A", "r")
    t2 = t.ljust(3, RText(".", "g"))
    assert t2.plain() == "A.."
    assert t2.runs[1][0] == "g"


def test_rjust():
    t = RText("A", "r")
    t2 = t.rjust(3, RText(".", "g"))
    assert t2.plain() == "..A"


def test_center():
    t = RText("A", "r")
    t2 = t.center(3, RText(".", "g"))
    assert t2.plain() == ".A."


# =========================================================
# TEXTBUFFER
# =========================================================

def test_buffer_add_string():
    buf = RBuffer()
    buf.add("Hello", "r")
    assert buf.to_text().runs == (("r", "Hello"),)


def test_buffer_add_text():
    buf = RBuffer()
    buf.add(RText("Hello", "r"))
    assert buf.to_text().runs == (("r", "Hello"),)


def test_buffer_add_run():
    buf = RBuffer()
    buf.run("r", "Hello")
    assert buf.to_text().runs == (("r", "Hello"),)


def test_buffer_merge_runs():
    buf = RBuffer()
    buf.add("A", "r")
    buf.add("B", "r")
    assert buf.to_text().runs == (("r", "AB"),)


def test_buffer_iadd():
    buf = RBuffer()
    buf += RText("Hello", "r")
    buf += " World"
    assert buf.to_text().plain() == "Hello World"


def test_buffer_extend_buffer():
    buf1 = RBuffer()
    buf1.add("Hello", "r")

    buf2 = RBuffer()
    buf2.add("World", "g")

    buf1.add(buf2)
    assert buf1.to_text().plain() == "HelloWorld"


# =========================================================
# ANSI RENDER
# =========================================================

def test_str_contains_ansi():
    t = RText("Hello", "r")
    s = str(t)
    assert "\033[" in s


# =========================================================
# EQUALITY
# =========================================================

def test_equality():
    t1 = RText("Hello", "r")
    t2 = RText("Hello", "r")
    assert t1.runs == t2.runs

def test_slice_preserves_style():
    t = RText.from_runs([
        ("r", "Hello"),
        ("g", "World"),
    ])
    s = t[3:8]
    assert s.plain() == "loWor"


def test_truncate_width():
    t = RText("Hello", "r")
    s = t.truncate(3)
    assert s.plain() == "Hel"


def test_wrap():
    t = RText("Hello World", "r")
    lines = t.wrap(5)
    assert lines[0].plain() == "Hello"
    assert lines[1].plain() == " Worl"
    assert lines[2].plain() == "d"