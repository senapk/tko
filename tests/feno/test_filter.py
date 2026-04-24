import pytest
from pathlib import Path
from tko.feno.filter import Filter, clean_com, get_comment, Mode

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
