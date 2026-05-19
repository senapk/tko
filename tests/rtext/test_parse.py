from tko.util.rt import RT


# ---------- texto simples ----------
def test_plain_text():
    t = RT.parse("hello world")
    assert t.plain() == "hello world"
    assert len(t.runs) == 1
    assert t.runs[0][0] == ""


# ---------- estilo simples ----------
def test_simple_style():
    t = RT.parse("[r]hello")
    assert t.plain() == "hello"
    assert t.runs[0][0] == "r"


# ---------- reset ----------
def test_reset():
    t = RT.parse("[r]hello[.] world")
    assert t.plain() == "hello world"
    assert t.runs[0][0] == "r"
    assert t.runs[1][0] == ""


# ---------- reset + estilo ----------
def test_reset_and_style():
    t = RT.parse("[r]red [.y]yellow")
    assert t.plain() == "red yellow"
    assert t.runs[0][0] == "r"
    assert t.runs[1][0] == "y"


# ---------- argumento string ----------
def test_argument_string():
    t = RT.parse("hello <$>", "world")
    assert t.plain() == "hello world"
    assert t.runs == (("", "hello world"),)


# ---------- argumento string com estilo ----------
def test_argument_with_style():
    t = RT.parse("[r]hello <$>", "world")
    assert t.runs == (("r", "hello world"),)


# ---------- argumento Text overlay ----------
def test_argument_text_overlay():
    name = RT("world", "y")
    t = RT.parse("[r]hello <$>", name)
    assert t.plain() == "hello world"
    assert "y" in t.runs[1][0]


# ---------- argumento Text overlay fg/bg ----------
def test_argument_style_overlay():
    name = RT("world", "B")
    t = RT.parse("[r]hello <$>", name)
    assert t.runs == (("r", "hello "), ("rB", "world"))


# ---------- argumento Text com reset ----------
def test_argument_text_after_reset():
    name = RT("world", "y")
    t = RT.parse("[r]hello [.]<$>", name)
    assert t.plain() == "hello world"
    assert t.runs[1][0] == "y"


# ---------- múltiplos argumentos ----------
def test_multiple_arguments():
    t = RT.parse("<$> + <$> = <$>", 1, 2, 3)
    assert t.plain() == "1 + 2 = 3"


# ---------- escape chaves ----------
def test_escape_braces():
    t = RT.parse("[[ hello ]]")
    assert t.plain() == "[ hello ]"


# ---------- estilos aninhados ----------
def test_nested_styles():
    t = RT.parse("[r]red [g]green [b]blue")
    assert t.plain() == "red green blue"
    assert t.runs[0][0] == "r"
    assert t.runs[1][0] == "g"
    assert t.runs[2][0] == "b"


# ---------- atributos ----------
def test_attributes():
    t = RT.parse("[r*_]hello")
    style = t.runs[0][0]
    assert "r" in style
    assert "*" in style
    assert "_" in style


# ---------- reverse ----------
def test_reverse():
    t = RT.parse("[X]hello")
    assert "X" in t.runs[0][0]


# ---------- bright ----------
def test_bright():
    t = RT.parse("[!r]hello")
    assert "r" in t.runs[0][0]
    assert "!" in t.runs[0][0]


# ---------- merge runs ----------
def test_merge_runs():
    t = RT.parse("[r]hello[r] world")
    assert len(t.runs) == 1


# ---------- estilo + argumento Text ----------
def test_style_plus_text_argument():
    name = RT("file.txt", "_")
    t = RT.parse("[r]open <$>", name)
    style = t.runs[1][0]
    assert "r" in style
    assert "_" in style


# ---------- reset dentro ----------
def test_reset_inside():
    t = RT.parse("[r]red [.]normal [g]green")
    assert t.runs[0][0] == "r"
    assert t.runs[1][0] == ""
    assert t.runs[2][0] == "g"
