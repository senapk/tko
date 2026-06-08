from tko.util.rt import RT
from tko.util.rt_style import RTStyle

def test_dollar_placeholder_string():
    t = RT.parse("ola, {}!".format("mundo"))
    assert t.plain() == "ola, mundo!"


def test_dollar_placeholder_multiple():
    t = RT.parse("{} + {} = {}".format(1, 2, 3))
    assert t.plain() == "1 + 2 = 3"


def test_dollar_placeholder_inherits_current_style():
    t = RT.parse("[r]erro: {}".format("arquivo"))
    assert t.plain() == "erro: arquivo"
    assert t.runs == ((RTStyle.parse("r"), "erro: arquivo"),)


def test_dollar_placeholder_rtext_merges_style():
    name = RT("file.txt", "_")
    t = RT.parse("[r]open {}".format(name.flat()))
    assert t.plain() == "open file.txt"
    assert t.runs == ((RTStyle.parse("r"), "open "), (RTStyle.parse("r_"), "file.txt"))

# ---------- [] e [.] resetam estilo ----------

def test_empty_brackets_reset_style():
    t = RT.parse("[r]erro[] ok")
    assert t.plain() == "erro ok"
    assert t.runs[0][0].fg == "r"
    assert t.runs[1][0].fg == None


def test_dot_brackets_reset_style():
    t = RT.parse("[r]erro[.] ok")
    assert t.plain() == "erro ok"
    assert t.runs[0][0].fg == "r"
    assert t.runs[1][0].fg == None


# ---------- reset + estilo [.xy] ----------

def test_dot_style_resets_then_applies():
    t = RT.parse("[r]red [.y]yellow")
    assert t.runs[0][0].fg == "r"
    assert t.runs[1][0].fg == "y"
