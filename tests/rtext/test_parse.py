from tko.util.rt import RT
from tko.util.rt_style import RTStyle


# ---------- texto simples ----------
def test_plain_text():
    t = RT.parse("hello world")
    assert t.plain() == "hello world"
    assert len(t.runs) == 1
    assert t.runs[0][0].fg is None


# ---------- estilo simples ----------
def test_simple_style():
    t = RT.parse("[r]hello")
    assert t.plain() == "hello"
    assert t.runs[0][0].fg == "r"


# ---------- reset ----------
def test_reset():
    t = RT.parse("[r]hello[.] world")
    assert t.plain() == "hello world"
    assert t.runs[0][0].fg == "r"
    assert t.runs[1][0].fg is None


# ---------- reset + estilo ----------
def test_reset_and_style():
    t = RT.parse("[r]red [.y]yellow")
    assert t.plain() == "red yellow"
    assert t.runs[0][0].fg == "r"
    assert t.runs[1][0].fg == "y"



# ---------- escape chaves ----------
def test_escape_braces():
    t = RT.parse("[[ hello ]]")
    assert t.plain() == "[ hello ]"


# ---------- estilos aninhados ----------
def test_nested_styles():
    t = RT.parse("[r]red [g]green [b]blue")
    assert t.plain() == "red green blue"
    assert t.runs[0][0].fg == "r"
    assert t.runs[1][0].fg == "g"
    assert t.runs[2][0].fg == "b"


# ---------- atributos ----------
def test_attributes():
    t = RT.parse("[r*_]hello")
    style = t.runs[0][0]
    assert "r" in style.to_tag()
    assert "*" in style.to_tag()
    assert "_" in style.to_tag()


# ---------- reverse ----------
def test_reverse():
    t = RT.parse("[X]hello")
    assert "X" in t.runs[0][0].to_tag()


# ---------- bright ----------
def test_bright():
    t = RT.parse("[!r]hello")
    assert "r" in t.runs[0][0].to_tag()
    assert "!" in t.runs[0][0].to_tag()


# ---------- merge runs ----------
def test_merge_runs():
    t = RT.parse("[r]hello[r] world")
    assert len(t.runs) == 1


def test_reset():
    t = RT.parse("[r]red[.]normal[]banana")
    assert t.runs[0] == (RTStyle.parse("r"), "red")
    assert t.runs[1] == (RTStyle.parse(""), "normal")
    assert t.runs[2] == (RTStyle.parse("r"), "banana")

def test_reset2():
    t = RT.parse("red[.]normal[]banana")
    assert len(t.runs) == 1
    assert t.runs[0] == (RTStyle.parse(""), "rednormalbanana")

def test_reset3():
    t = RT.parse("[b]red[.b]normal[]banana")
    assert t.runs == (
        (RTStyle.parse("b"), "rednormalbanana"),
    )

# ---------- reset dentro ----------
def test_reset_inside():
    t = RT.parse("[r]red [.]normal [g]green")
    assert t.runs[0][0].fg == "r"
    assert t.runs[1][0].fg is None
    assert t.runs[2][0].fg == "g"
