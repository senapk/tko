from tko.util.rtext import RText


# ---------- [$] como placeholder posicional ----------

def test_dollar_placeholder_string():
    t = RText.parse("ola, [$]!", "mundo")
    assert t.plain() == "ola, mundo!"


def test_dollar_placeholder_multiple():
    t = RText.parse("[$] + [$] = [$]", 1, 2, 3)
    assert t.plain() == "1 + 2 = 3"


def test_dollar_placeholder_inherits_current_style():
    t = RText.parse("[r]erro: [$]", "arquivo")
    assert t.plain() == "erro: arquivo"
    assert t.runs == (("r", "erro: arquivo"),)


def test_dollar_placeholder_rtext_merges_style():
    name = RText("file.txt", "_")
    t = RText.parse("[r]open [$]", name)
    assert t.plain() == "open file.txt"
    assert "r" in t.runs[1][0]
    assert "_" in t.runs[1][0]


def test_dollar_placeholder_tuple_arg():
    t = RText.parse("val: [$]", ("g", "ok"))
    assert t.plain() == "val: ok"
    assert "g" in t.runs[1][0]


# ---------- [] e [.] resetam estilo ----------

def test_empty_brackets_reset_style():
    t = RText.parse("[r]erro[] ok")
    assert t.plain() == "erro ok"
    assert t.runs[0][0] == "r"
    assert t.runs[1][0] == ""


def test_dot_brackets_reset_style():
    t = RText.parse("[r]erro[.] ok")
    assert t.plain() == "erro ok"
    assert t.runs[0][0] == "r"
    assert t.runs[1][0] == ""


# ---------- reset + estilo [.xy] ----------

def test_dot_style_resets_then_applies():
    t = RText.parse("[r]red [.y]yellow")
    assert t.runs[0][0] == "r"
    assert t.runs[1][0] == "y"


# ---------- placeholder após reset ----------

def test_dollar_after_reset_no_style():
    name = RText("world", "y")
    t = RText.parse("[r]hello [.][$]", name)
    assert t.plain() == "hello world"
    assert t.runs[1][0] == "y"


# ---------- escape [[ e ]] ----------

def test_escape_double_brackets():
    t = RText.parse("[[ hello ]]")
    assert t.plain() == "[ hello ]"
