from tko.util.rt import RT

def test_dollar_placeholder_string():
    t = RT.parse("ola, {}!".format("mundo"))
    assert t.plain() == "ola, mundo!"


def test_dollar_placeholder_multiple():
    t = RT.parse("{} + {} = {}".format(1, 2, 3))
    assert t.plain() == "1 + 2 = 3"


def test_dollar_placeholder_inherits_current_style():
    t = RT.parse("[r]erro: {}".format("arquivo"))
    assert t.plain() == "erro: arquivo"
    assert t.runs == (("r", "erro: arquivo"),)


def test_dollar_placeholder_rtext_merges_style():
    name = RT("file.txt", "_")
    t = RT.parse("[r]open {}".format(name))
    assert t.plain() == "open file.txt"
    assert "r" in t.runs[1][0].to_tag()
    assert "_" in t.runs[1][0].to_tag()

# ---------- [] e [.] resetam estilo ----------

def test_empty_brackets_reset_style():
    t = RT.parse("[r]erro[] ok")
    assert t.plain() == "erro ok"
    assert t.runs[0][0].fg == "r"
    assert t.runs[1][0].fg == ""


def test_dot_brackets_reset_style():
    t = RT.parse("[r]erro[.] ok")
    assert t.plain() == "erro ok"
    assert t.runs[0][0].fg == "r"
    assert t.runs[1][0].fg == ""


# ---------- reset + estilo [.xy] ----------

def test_dot_style_resets_then_applies():
    t = RT.parse("[r]red [.y]yellow")
    assert t.runs[0][0].fg == "r"
    assert t.runs[1][0].fg == "y"
