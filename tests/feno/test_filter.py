from pathlib import Path
from tko.feno.filter import Filter, clean_com, get_comment

def test_get_comment():
    assert get_comment(Path("script.py")) == "#"
    assert get_comment(Path("script.hs")) == "--"
    assert get_comment(Path("script.puml")) == "'"
    assert get_comment(Path("script.c")) == "//"
    assert get_comment(Path("script.java")) == "//"

def test_clean_com():
    content = "print('a')\n# print('b')\n  # print('c')\nprint('d')"
    out = clean_com(Path("test.py"), content)
    assert out == "print('a')\nprint('d')"

def test_filter_default_add():
    content = "def foo():\n    print('a')\n"
    f = Filter(Path("test.py"))
    out = f.process(content)
    assert out == "def foo():\n    print('a')\n"

def test_filter_del_mode():
    content = """def foo():
    # DEL!
    print("hidden")
    print("also hidden")
def bar():
    print("visible")
"""
    f = Filter(Path("test.py"))
    out = f.process(content)
    expected = """def foo():
def bar():
    print("visible")
"""
    assert out == expected

def test_filter_com_mode():
    content = """def foo():
    # COM!
    print("a")
    print("b")
def bar():
    print("c")
"""
    f = Filter(Path("test.py"))
    out = f.process(content)
    expected = """def foo():
    # print("a")
    # print("b")
def bar():
    print("c")
"""
    assert out == expected

def test_filter_act_mode():
    content = """def foo():
    # ACT!
    # print("a")
    # print("b")
def bar():
    print("c")
"""
    f = Filter(Path("test.py"))
    out = f.process(content)
    expected = """def foo():
    print("a")
    print("b")
def bar():
    print("c")
"""
    assert out == expected

def test_filter_temp_del():
    content = """def foo():
    print("hide this") # DEL!
    print("show this")
"""
    f = Filter(Path("test.py"))
    out = f.process(content)
    expected = """def foo():
    print("show this")
"""
    assert out == expected

def test_filter_temp_com():
    content = """def foo():
    print("comment this") # COM!
    print("show this")
"""
    f = Filter(Path("test.py"))
    out = f.process(content)
    expected = """def foo():
    # print("comment this")
    print("show this")
"""
    assert out == expected

def test_filter_nested_scopes():
    content = """def foo():
    # DEL!
    if True:
        print("hidden")
        # ADD!
        print("visible inside hidden")
    print("also hidden")
def bar():
    print("visible")
"""
    f = Filter(Path("test.py"))
    out = f.process(content)
    expected = """def foo():
        print("visible inside hidden")
def bar():
    print("visible")
"""
    assert out == expected

def test_filter_c_style():
    content = """int main() {
    // DEL!
    printf("hidden\\n");
    // ADD!
    printf("visible\\n");
}
"""
    f = Filter(Path("test.c"))
    out = f.process(content)
    expected = """int main() {
    printf("visible\\n");
}
"""
    assert out == expected


def test_filter_block_keep():
    content = """def foo():
    # @KEEP
    print("kept 1")
    print("kept 2")
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """def foo():
    print("kept 1")
    print("kept 2")
"""


def test_filter_block_drop():
    content = """def foo():
    # @DROP
    print("dropped 1")
    print("dropped 2")
def bar():
    print("kept")
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """def foo():
def bar():
    print("kept")
"""


def test_filter_block_com():
    content = """def foo():
    # @COM
    print("comment 1")
    print("comment 2")
def bar():
    print("kept")
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """def foo():
    # print("comment 1")
    # print("comment 2")
def bar():
    print("kept")
"""


def test_filter_block_unc():
    content = """def foo():
    # @UNC
    # print("uncomment 1")
    # print("uncomment 2")
def bar():
    # print("stays comment")
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """def foo():
    print("uncomment 1")
    print("uncomment 2")
def bar():
    # print("stays comment")
"""


def test_filter_inline_new_syntax():
    content = """a = 1  # @KEEP
b = 2  # @DROP
c = 3  # @COM
# d = 4  # @UNC
e = 5
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """a = 1
# c = 3
d = 4
e = 5
"""


def test_filter_inline_legacy_syntax():
    content = """a = 1  # ADD!
b = 2  # DEL!
c = 3  # COM!
# d = 4  # ACT!
e = 5
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """a = 1
# c = 3
d = 4
e = 5
"""


def test_filter_nested_scopes_new_syntax():
    content = """def foo():
    # @DROP
    if True:
        print("hidden")
        # @KEEP
        print("visible inside hidden")
    print("also hidden")
def bar():
    print("visible")
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """def foo():
        print("visible inside hidden")
def bar():
    print("visible")
"""


def test_filter_deep_nested_and_return():
    content = """print("0a")
if a:
    # @DROP
    print("1a")
    if b:
        # @KEEP
        print("2a")
        if c:
            # @COM
            print("3a")
        print("2b")
    print("1b")
print("0b")
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """print("0a")
if a:
        print("2a")
        if c:
            # print("3a")
        print("2b")
print("0b")
"""


def test_filter_consecutive_operators_same_indent():
    content = """def foo():
    # @DROP
    print("dropped")
    # @COM
    print("commented")
    # @KEEP
    print("kept")
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """def foo():
    # print("commented")
    print("kept")
"""


def test_filter_tabs_indentation():
    content = """func foo() {
\t// @DROP
\tif true {
\t\tprintln("hidden")
\t\t// @KEEP
\t\tprintln("visible")
\t}
\tprintln("also hidden")
}
"""
    f = Filter(Path("test.go"))
    assert f.process(content) == """func foo() {
\t\tprintln("visible")
}
"""


def test_filter_tabs_comment_and_uncomment():
    content = """\t// @COM
\tx = 1
\t\ty = 2
\t// @UNC
\t// z = 3
\t\t// w = 4
"""
    f = Filter(Path("test.go"))
    assert f.process(content) == """\t// x = 1
\t\t// y = 2
\tz = 3
\t\tw = 4
"""


def test_filter_strings_containing_operator_names():
    content = """s1 = "hello # @DROP world"
s2 = 'not a tag # @KEEP'
s3 = "ADD! and DEL!"
s4 = "inside # @DROP"  # @DROP
s5 = "keep this # @COM"  # @KEEP
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """s1 = "hello # @DROP world"
s2 = 'not a tag # @KEEP'
s3 = "ADD! and DEL!"
s5 = "keep this # @COM"
"""


def test_filter_c_style_strings_false_positives():
    content = """printf("// @DROP is not a comment\\n");
char *p = "// ADD! string";
printf("test\\n"); // @DROP
"""
    f = Filter(Path("test.c"))
    assert f.process(content) == """printf("// @DROP is not a comment\\n");
char *p = "// ADD! string";
"""


def test_filter_other_comment_styles():
    # Haskell with --
    hs_content = """main = do
    -- @DROP
    putStrLn "hidden"
    -- @KEEP
    putStrLn "visible"
"""
    f_hs = Filter(Path("test.hs"))
    assert f_hs.process(hs_content) == """main = do
    putStrLn "visible"
"""

    # PlantUML with '
    puml_content = """@startuml
' @DROP
Alice -> Bob: hidden
' @KEEP
Alice -> Bob: visible
@enduml
"""
    f_puml = Filter(Path("test.puml"))
    assert f_puml.process(puml_content) == """@startuml
Alice -> Bob: visible
@enduml
"""


def test_filter_empty_lines_and_content():
    assert Filter(Path("test.py")).process("") == ""
    assert Filter(Path("test.py")).process("\n\n") == "\n\n"

    content = """def foo():
    # @COM
    x = 1

    y = 2
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """def foo():
    # x = 1

    # y = 2
"""


def test_filter_inline_overrides_block_mode():
    content = """def foo():
    # @COM
    x = 1
    y = 2  # @KEEP
    z = 3  # @DROP
    w = 4
"""
    f = Filter(Path("test.py"))
    assert f.process(content) == """def foo():
    # x = 1
    y = 2
    # w = 4
"""

