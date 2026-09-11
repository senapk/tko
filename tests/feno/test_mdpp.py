from loguru import logger
from pathlib import Path
from tko.feno.mdpp import TocMaker, Toc, TocTable, Toch, Load, Links, Tests, Action, Mdpp

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

def test_toc_multiple_heading_levels():
    content = """# Root (ignored from level 1)
<!-- toc -->
<!-- toc -->
## Level 2A
### Level 3A
#### Level 4A
## Level 2B
### Level 3B
"""
    out = Toc.execute(content, Action.RUN)
    assert "- [Level 2A](#level-2a)" in out
    assert "  - [Level 3A](#level-3a)" in out
    assert "    - [Level 4A](#level-4a)" in out
    assert "- [Level 2B](#level-2b)" in out
    assert "[Root]" not in out

def test_toc_table_execute():
    content = """# Main
<!-- toc-table -->
<!-- toc-table -->
## Sec 1
### Sub 1
## Sec 2
"""
    expected = """# Main
<!-- toc-table -->
[Sec 1](#sec-1) | [Sec 2](#sec-2)
-- | --
<!-- toc-table -->
## Sec 1
### Sub 1
## Sec 2
"""
    out = TocTable.execute(content, Action.RUN)
    assert out == expected

def test_toc_table_execute_clean():
    content = """# Main
<!-- toc-table -->
[Sec 1](#sec-1)
--
<!-- toc-table -->
## Sec 1
"""
    expected = """# Main
<!-- toc-table -->
<!-- toc-table -->
## Sec 1
"""
    out = TocTable.execute(content, Action.CLEAN)
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

def test_load_rm_comments_and_rmcom():
    content = "print('a')\n# print('b')\nprint('c')"
    out1 = Load.rm_comments(Path("test.py"), content)
    out2 = Load.rmcom(Path("test.py"), content)
    assert out1 == "print('a')\nprint('c')"
    assert out2 == out1

def test_load_rmcom_multiple_suffixes():
    c_style = "run();\n// hide\nshow();"
    puml_style = "@startuml\n' hide\n@enduml"
    assert Load.rm_comments(Path("main.c"), c_style) == "run();\nshow();"
    assert Load.rm_comments(Path("diag.puml"), puml_style) == "@startuml\n@enduml"

def test_load_parse_tags_and_warnings():
    messages: list[str] = []

    sink_id = logger.add(
        messages.append,
        level="WARNING",
        format="{message}",
    )

    try:
        params = Load.parse_tags("--fenced --rm-comments --filter")

        assert params.fenced == ""
        assert params.rm_comments is True
        assert params.filter is True

        Load.parse_tags("--unknown")

        text = "\n".join(messages)

        assert "tag não reconhecida '--unknown'" in text

    finally:
        logger.remove(sink_id)

def test_load_rejects_removed_test_options():
    messages: list[str] = []
    sink_id = logger.add(messages.append, level="ERROR", format="{message}")
    try:
        Load.parse_tags("--tests --tests-table --tests-tio")
        text = "\n".join(messages)
        assert "a opção --tests não é suportada em load" in text
        assert "a opção --tests-table não é suportada em load" in text
        assert "a opção --tests-tio não é suportada em load" in text
    finally:
        logger.remove(sink_id)

def test_load_rejects_removed_extract_option():
    messages: list[str] = []
    sink_id = logger.add(messages.append, level="ERROR", format="{message}")
    try:
        Load.parse_tags("--extract solution")
        assert "a opção --extract não é suportada em load" in "\n".join(messages)
    finally:
        logger.remove(sink_id)

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
    out = Load.generate_tests_table_from_toml(toml_content, tmp_path / "cases.toml")
    assert out.count("<table>") == 2
    assert "Entrada" in out
    assert "Saída" in out
    assert "1\n2\n" in out
    assert "b\nc\n" in out

def test_generate_table_from_test_toml_all_cases_with_multiline_content(tmp_path: Path):
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
    out = Load.generate_tests_table_from_toml(toml_content, tmp_path / "cases.toml")
    assert out.count("<table>") == 2
    assert "left\n" in out
    assert "right\n" in out
    assert "second\n" in out

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

def test_load_execute_missing_file(tmp_path: Path):
    messages: list[str] = []

    sink_id = logger.add(
        messages.append,
        level="WARNING",
        format="{message}",
    )

    try:
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

        text = "\n".join(messages)

        assert "arquivo missing.py não encontrado" in text

    finally:
        logger.remove(sink_id)

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

def test_tests_execute_renders_all_cases_and_honors_limit(tmp_path: Path):
    toml_file = tmp_path / "tests.toml"
    toml_file.write_text("""[[tests]]
input = "10"
output = "20"
[[tests]]
input = "30"
output = "40"
[[tests]]
input = "50"
output = "60"
[[tests]]
input = "70"
output = "80"
[[tests]]
input = "90"
output = "100"
""")
    content = """<!-- tests tests.toml -->
<!-- tests -->

<!-- tests tests.toml --limit 2 -->
<!-- tests -->

<!-- tests tests.toml --limit 0 -->
<!-- tests -->
"""
    out = Tests.execute(content, tmp_path, Action.RUN)
    blocks = out.split("<!-- tests -->")
    assert blocks[0].count("<table>") == 5
    assert blocks[1].count("<table>") == 2
    assert blocks[2].count("<table>") == 5

    cleaned = Tests.execute(out, tmp_path, Action.CLEAN)
    assert cleaned == """<!-- tests tests.toml -->
<!-- tests -->

<!-- tests tests.toml --limit 2 -->
<!-- tests -->

<!-- tests tests.toml --limit 0 -->
<!-- tests -->
"""

def test_tests_execute_expands_loaded_cases_and_warns_on_invalid_limit(tmp_path: Path):
    cases = tmp_path / "cases.toml"
    cases.write_text("""[[tests]]
input = "one"
output = "1"
[[tests]]
input = "two"
output = "2"
""")
    root = tmp_path / "tests.toml"
    root.write_text('load = "cases.toml"\n')
    messages: list[str] = []
    sink_id = logger.add(messages.append, level="WARNING", format="{message}")
    try:
        content = """<!-- tests tests.toml --limit nope -->
<!-- tests -->
"""
        out = Tests.execute(content, tmp_path, Action.RUN)
        assert out.count("<table>") == 2
        assert "valor inválido ou faltando para --limit" in "\n".join(messages)
    finally:
        logger.remove(sink_id)

def test_load_execute_fenced_explicit_lang(tmp_path: Path):
    data_file = tmp_path / "query.txt"
    data_file.write_text("SELECT * FROM users;\n")
    content = """<!-- load query.txt --fenced sql -->
<!-- load -->
"""
    out = Load.execute(content, tmp_path, Action.RUN)
    assert "```sql\nSELECT * FROM users;\n```" in out

def test_load_pipeline_order_invariance(tmp_path: Path):
    py_file = tmp_path / "full.py"
    py_file.write_text("""# @KEEP
keep_var = 1
# @DROP
drop_var = 2
# Comment line
result = keep_var
""")
    content1 = """<!-- load full.py --filter --rm-comments --fenced py -->
<!-- load -->
"""
    content2 = """<!-- load full.py --fenced py --rm-comments --filter -->
<!-- load -->
"""
    out1 = Load.execute(content1, tmp_path, Action.RUN)
    out2 = Load.execute(content2, tmp_path, Action.RUN)
    assert out1.replace("full.py --filter --rm-comments --fenced py", "CMD") == \
           out2.replace("full.py --fenced py --rm-comments --filter", "CMD")
    assert "keep_var = 1" in out1
    assert "drop_var = 2" not in out1
    assert "# Comment line" not in out1
    assert "```py" in out1

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
    dummy_file = target_dir / "README.md"
    
    out = Links.execute(dummy_file, content, Action.RUN)
    expected = """# Main
<!-- links my_links -->
- [page1.md](my_links/page1.md)
- [page2.md](my_links/page2.md)
<!-- links -->
"""
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

def test_mdpp_update_file_full_workflow(tmp_path: Path):
    (tmp_path / "helper.py").write_text("def add(a, b):\n    return a + b\n")
    (tmp_path / "tests.toml").write_text("""[[tests]]
input = "1 2"
output = "3"
""")
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "guide.md").write_text("# Guide\n")

    readme = tmp_path / "README.md"
    readme.write_text("""# Project Title

<!-- toc -->
<!-- toc -->

<!-- toc-table -->
<!-- toc-table -->

## Overview

<!-- load helper.py --fenced -->
<!-- load -->

## Tests

<!-- tests tests.toml -->
<!-- tests -->

## Documentation

<!-- links docs -->
<!-- links -->

""")

    modified = Mdpp.update_file(readme, Action.RUN)
    assert modified is True
    content = readme.read_text()
    assert "- [Overview](#overview)" in content
    assert "[Overview](#overview) | [Tests](#tests) | [Documentation](#documentation)" in content
    assert "def add(a, b):" in content
    assert "<table>" in content
    assert "- [guide.md](docs/guide.md)" in content
    # Now test CLEAN mode
    cleaned = Mdpp.update_file(readme, Action.CLEAN)
    assert cleaned is True
    clean_content = readme.read_text()
    assert "def add" not in clean_content
    assert "<table>" not in clean_content
    assert "<!-- toc -->\n<!-- toc -->" in clean_content
    assert "<!-- toc-table -->\n<!-- toc-table -->" in clean_content
    assert "<!-- links docs -->\n<!-- links -->" in clean_content
