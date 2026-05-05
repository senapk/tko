from pathlib import Path
from tko.feno.mdpp import TocMaker, Toc, Toch, Load, Links, Action, Save

def test_toc_maker_get_md_link():
    assert TocMaker.get_md_link("## Hello World") == "hello-world"
    assert TocMaker.get_md_link("# Some_Title") == "some_title"
    assert TocMaker.get_md_link("### Title With <!-- comment -->") == "title-with-"
    assert TocMaker.get_md_link("## Title [](link)") == "title-"
    assert TocMaker.get_md_link(None) == ""
    assert TocMaker.get_md_link("## C\\Cpp - Basics") == "ccpp---basics"

def test_toc_maker_remove_code_fences():
    content = "a\n```python\n# skip this\n```\nb"
    out = TocMaker.remove_code_fences(content)
    assert out == "a\nb"


def test_toc_maker_extract_entries_ignores_code_and_disable_tag():
    content = """# Main
## Keep me
```md
## Hidden in code block
```
## Skip []()
"""
    out = TocMaker.extract_entries(content)
    assert out == [
        (1, "[Main](#main)"),
        (2, "[Keep me](#keep-me)"),
    ]

def test_toc_execute():
    content = """# Main
<!-- toc -->
<!-- toc -->
## Sec 1
### Sub 1
## Sec 2
"""
    expected = """# Main
<!-- toc -->
- [Sec 1](#sec-1)
  - [Sub 1](#sub-1)
- [Sec 2](#sec-2)
<!-- toc -->
## Sec 1
### Sub 1
## Sec 2
"""
    out = Toc.execute(content, Action.RUN)
    assert out == expected

def test_toc_execute_clean():
    content = """# Main
<!-- toc -->
- [Sec 1](#sec-1)
<!-- toc -->
## Sec 1
"""
    expected = """# Main
<!-- toc -->
<!-- toc -->
## Sec 1
"""
    out = Toc.execute(content, Action.CLEAN)
    assert out == expected

def test_toch_execute():
    content = """# Main
<!-- toch -->
<!-- toch -->
## Sec 1
### Sub 1
## Sec 2
"""
    expected = """# Main
<!-- toch -->
[Sec 1](#sec-1) | [Sec 2](#sec-2)
-- | --
<!-- toch -->
## Sec 1
### Sub 1
## Sec 2
"""
    out = Toch.execute(content, Action.RUN)
    assert out == expected


def test_toch_execute_clean():
    content = """# Main
<!-- toch -->
[Sec 1](#sec-1)
--
<!-- toch -->
## Sec 1
"""
    expected = """# Main
<!-- toch -->
<!-- toch -->
## Sec 1
"""
    out = Toch.execute(content, Action.CLEAN)
    assert out == expected

def test_load_rmcom():
    content = "print('a')\n# print('b')\nprint('c')"
    out = Load.rmcom(Path("test.py"), content)
    assert out == "print('a')\nprint('c')"


def test_load_rmcom_multiple_suffixes():
    c_style = "run();\n// hide\nshow();"
    puml_style = "@startuml\n' hide\n@enduml"
    assert Load.rmcom(Path("main.c"), c_style) == "run();\nshow();"
    assert Load.rmcom(Path("diag.puml"), puml_style) == "@startuml\n@enduml"

def test_load_extract_between_tags():
    content = "a\n[[tag]]\nb\nc\n[[tag]]\nd"
    out = Load.extract_between_tags(content, "tag")
    assert out == "b\nc\n"


def test_load_parse_tags_and_warnings(capsys):
    params = Load.parse_tags("--fenced --extract sec --rmcom --filter --tests 2")
    assert params.fenced == ""
    assert params.extract == "sec"
    assert params.rmcom is True
    assert params.filter is True
    assert params.tests == 2

    invalid = Load.parse_tags("--extract --tests nope --unknown")
    assert invalid.extract is None
    assert invalid.tests is None
    out = capsys.readouterr().out
    assert "missing value for --extract" in out
    assert "invalid or missing integer for --tests" in out
    assert "unrecognized tag '--unknown'" in out


def test_generate_table_from_test_toml_all_cases(tmp_path: Path):
    toml_content = """[[tests]]
input = '''
1
2
'''
output = '''
3
'''

[[tests]]
input = '''
a
'''
output = '''
b
c
'''
"""
    out = Load.generate_tests_from_test_toml(toml_content, tmp_path / "cases.toml", 0, True)
    assert out.count("<table>") == 2
    assert "Entrada" in out
    assert "Saída" in out
    assert "1\n2\n" in out
    assert "b\nc\n" in out


def test_generate_table_from_test_toml_limited_cases(tmp_path: Path):
    toml_content = """[[tests]]
input = '''
left
'''
output = '''
right
'''

[[tests]]
input = '''
second
'''
output = '''
case
'''
"""
    out = Load.generate_tests_from_test_toml(toml_content, tmp_path / "cases.toml", 1, False)
    assert out.count("<table>") == 0
    assert "```py" in out
    assert ">>>>>>>> INSERT" in out
    assert "======== EXPECT" in out
    assert "<<<<<<<< FINISH" in out
    assert "left\n" in out
    assert "right\n" in out
    assert "second\n" not in out

def test_load_execute(tmp_path: Path):
    target_dir = tmp_path
    
    file1 = tmp_path / "script.py"
    file1.write_text("print('hello')\n")
    
    content = """# Main
<!-- load script.py --fenced -->
<!-- load -->
"""
    out = Load.execute(content, target_dir, Action.RUN)
    expected = """# Main
<!-- load script.py --fenced -->
```py
print('hello')

```
<!-- load -->
"""
    assert out == expected


def test_load_execute_clean(tmp_path: Path):
    content = """# Main
<!-- load script.py --fenced -->
```py
print('old')
```
<!-- load -->
"""
    out = Load.execute(content, tmp_path, Action.CLEAN)
    expected = """# Main
<!-- load script.py --fenced -->
<!-- load -->
"""
    assert out == expected


def test_load_execute_missing_file(tmp_path: Path, capsys):
    content = """# Main
<!-- load missing.py -->
something stale
<!-- load -->
"""
    out = Load.execute(content, tmp_path, Action.RUN)
    expected = """# Main
<!-- load missing.py -->

<!-- load -->
"""
    assert out == expected
    assert "file missing.py not found" in capsys.readouterr().out


def test_load_execute_multiple_blocks(tmp_path: Path):
    (tmp_path / "a.py").write_text("print('a')\n")
    (tmp_path / "b.py").write_text("print('b')\n")
    content = """<!-- load a.py --fenced -->
<!-- load -->

<!-- load b.py --fenced -->
<!-- load -->
"""
    out = Load.execute(content, tmp_path, Action.RUN)
    assert "print('a')" in out
    assert "print('b')" in out
    assert out.count("```py") == 2

def test_links_execute(tmp_path: Path):
    target_dir = tmp_path / "readme_dir"
    target_dir.mkdir()
    
    sub_dir = target_dir / "my_links"
    sub_dir.mkdir()
    
    (sub_dir / "page1.md").write_text("page1")
    (sub_dir / "page2.md").write_text("page2")
    
    content = """# Main
<!-- links my_links -->
<!-- links -->
"""
    # Create dummy file path to resolve relative paths
    dummy_file = target_dir / "README.md"
    
    out = Links.execute(dummy_file, content, Action.RUN)
    expected = """# Main
<!-- links my_links -->
- [page1.md](my_links/page1.md)
- [page2.md](my_links/page2.md)
<!-- links -->
"""
    # Replace backslashes for windows compatibility in test assertion if needed, but the implementation uses replace("\\", "/")
    assert out == expected


def test_links_execute_clean(tmp_path: Path):
    readme = tmp_path / "README.md"
    content = """# Main
<!-- links docs -->
- [old.md](docs/old.md)
<!-- links -->
"""
    out = Links.execute(readme, content, Action.CLEAN)
    expected = """# Main
<!-- links docs -->
<!-- links -->
"""
    assert out == expected


def test_links_load_links_nested_and_ignores_hidden(tmp_path: Path):
    root = tmp_path / "readme"
    root.mkdir()
    docs = root / "docs"
    docs.mkdir()
    (docs / "a.md").write_text("a")
    (docs / ".hidden.md").write_text("x")
    child = docs / "sub"
    child.mkdir()
    (child / "b.md").write_text("b")
    out = Links.load_links(root, Path("docs"))
    assert "- [a.md](docs/a.md)" in out
    assert "- sub" in out
    assert "- [b.md](docs/sub/b.md)" in out
    assert ".hidden.md" not in out

def test_save_execute(tmp_path: Path):
    content = f"""
[](save)[]({tmp_path}/output.txt)
```text
saved content
```
[](save)
"""
    Save.execute(content)
    assert (tmp_path / "output.txt").read_text() == "saved content\n"


def test_save_execute_skips_unchanged(tmp_path: Path, capsys):
    content = f"""
[](save)[]({tmp_path}/output.txt)
```text
saved content
```
[](save)
"""
    Save.execute(content)
    first = capsys.readouterr().out
    assert "updated" in first

    Save.execute(content)
    second = capsys.readouterr().out
    assert second == ""
