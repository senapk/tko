from tko.util.rbuffer import RBuffer
from tko.util.rt import RT, RenderMode
from tko.util.text_style import TextStyle


# =========================================================
# PARSE
# =========================================================

def test_parse_plain():
    t = RT.parse("hello")
    assert t.plain() == "hello"
    assert t.runs == ((TextStyle.parse(""), "hello"),)


def test_parse_style():
    t = RT.parse("[r]hello")
    assert t.runs == ((TextStyle.parse("r"), "hello"),)


def test_parse_reset():
    t = RT.parse("[r]hello[.] world")
    assert t.runs == ((TextStyle.parse("r"), "hello"), (TextStyle.parse(""), " world"))


def test_parse_overlay():
    t = RT.parse("[r]red [B]blue")
    # overlay -> rB
    assert t.runs == ((TextStyle.parse("r"), "red "), (TextStyle.parse("rB"), "blue"))


def test_parse_reset_overlay():
    t = RT.parse("[r]red [.B]blue")
    assert t.runs == ((TextStyle.parse("r"), "red "), (TextStyle.parse("B"), "blue"))



def test_parse_escape():
    t = RT.parse("[[ hello ]]")
    assert t.plain() == "[ hello ]"


# =========================================================
# TEXT BASIC
# =========================================================

def test_concat():
    t = RT("A", "r") + RT("B", "g")
    assert t.plain() == "AB"
    assert len(t.runs) == 2


def test_merge_runs():
    t = RT("A", "r") + RT("B", "r")
    assert len(t.runs) == 1
    assert t.runs[0] == (TextStyle.parse("r"), "AB")


def test_len():
    t = RT("hello", "r")
    assert len(t) == 5


def test_plain():
    t = RT.parse("[r]hello[.] world")
    assert t.plain() == "hello world"


# =========================================================
# STRING METHODS
# =========================================================

def test_upper():
    t = RT("hello", "r").upper()
    assert t.runs == ((TextStyle.parse("r"), "HELLO"),)


def test_lower():
    t = RT("HELLO", "r").lower()
    assert t.runs == ((TextStyle.parse("r"), "hello"),)


def test_replace_simple():
    t = RT.parse("hello world")
    t2 = t.replace("world", "there", "r")
    assert t2.plain() == "hello there"


def test_replace_across_runs():
    t = RT.from_runs([
        (TextStyle.parse("r"), "Hel"),
        (TextStyle.parse("g"), "lo Wo"),
        (TextStyle.parse("y"), "rld"),
    ])
    t2 = t.replace("lo Wo", "X", "b")
    assert t2.plain() == "HelXrld"


# =========================================================
# SPLIT
# =========================================================

def test_split_preserve_style():
    t = RT.from_runs([
        (TextStyle.parse("r"), "Hello"),
        (TextStyle.parse(""), " "),
        (TextStyle.parse("g"), "World"),
    ])
    parts = t.split(" ")
    assert parts[0].runs == ((TextStyle.parse("r"), "Hello"),)
    assert parts[1].runs == ((TextStyle.parse("g"), "World"),)


# =========================================================
# ALIGN
# =========================================================

def test_ljust():
    t = RT("A", "r")
    t2 = t.ljust(3, RT(".", "g"))
    assert t2.plain() == "A.."
    assert t2.runs == ((TextStyle.parse("r"), "A"), (TextStyle.parse("g"), ".."))


def test_rjust():
    t = RT("A", "r")
    t2 = t.rjust(3, RT(".", "g"))
    assert t2.plain() == "..A"


def test_center():
    t = RT("A", "r")
    t2 = t.center(3, RT(".", "g"))
    assert t2.plain() == ".A."


# =========================================================
# TEXTBUFFER
# =========================================================

def test_buffer_add_string():
    buf = RBuffer()
    buf.add("Hello", "r")
    assert buf.to_rt().runs == ((TextStyle.parse("r"), "Hello"),)


def test_buffer_rb_renders_blue_foreground_red_background():
    buf = RBuffer()
    buf.add("Hello", "Rb")

    assert buf.to_rt().runs == ((TextStyle.parse("bR"), "Hello"),)
    assert buf.to_rt().render(RenderMode.ANSI) == "\033[34;41mHello\033[0m"


def test_buffer_add_text():
    buf = RBuffer()
    buf.add(RT("Hello", "r"))
    assert buf.to_rt().runs == ((TextStyle.parse("r"), "Hello"),)


def test_buffer_add_run():
    buf = RBuffer()
    buf.run(TextStyle.parse("r"), "Hello")
    assert buf.to_rt().runs == ((TextStyle.parse("r"), "Hello"),)


def test_buffer_merge_runs():
    buf = RBuffer()
    buf.add("A", "r")
    buf.add("B", "r")
    assert buf.to_rt().runs == ((TextStyle.parse("r"), "AB"),)


def test_buffer_iadd():
    buf = RBuffer()
    buf += RT("Hello", "r")
    buf += " World"
    assert buf.to_rt().plain() == "Hello World"


def test_buffer_extend_buffer():
    buf1 = RBuffer()
    buf1.add("Hello", "r")

    buf2 = RBuffer()
    buf2.add("World", "g")

    buf1.add(buf2)
    assert buf1.to_rt().plain() == "HelloWorld"


# =========================================================
# EQUALITY
# =========================================================

def test_equality():
    t1 = RT("Hello", "r")
    t2 = RT("Hello", "r")
    assert t1.runs == t2.runs

def test_slice_preserves_style():
    t = RT.from_runs([
        (TextStyle.parse("r"), "Hello"),
        (TextStyle.parse("g"), "World"),
    ])
    s = t[3:8]
    assert s.plain() == "loWor"


def test_truncate_width():
    t = RT("Hello", "r")
    s = t.truncate(3)
    assert s.plain() == "Hel"


def test_wrap():
    t = RT("Hello World", "r")
    lines = t.wrap(5)
    assert lines[0].plain() == "Hello"
    assert lines[1].plain() == " Worl"
    assert lines[2].plain() == "d"
