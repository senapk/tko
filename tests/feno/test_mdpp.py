from pathlib import Path
from tko.feno.mdpp import TocMaker, Toc, Toch, Load, Links, Action, Save

def test_toc_maker_get_md_link():
    assert TocMaker.get_md_link("## Hello World") == "hello-world"
    assert TocMaker.get_md_link("# Some_Title") == "some_title"
    assert TocMaker.get_md_link("### Title With <!-- comment -->") == "title-with-"
    assert TocMaker.get_md_link("## Title [](link)") == "title-"

def test_toc_maker_remove_code_fences():
    content = "a\n```python\n# skip this\n```\nb"
    out = TocMaker.remove_code_fences(content)
    assert out == "a\nb"

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

def test_load_rmcom():
    content = "print('a')\n# print('b')\nprint('c')"
    out = Load.rmcom("test.py", content)
    assert out == "print('a')\nprint('c')"

def test_load_extract_between_tags():
    content = "a\n[[tag]]\nb\nc\n[[tag]]\nd"
    out = Load.extract_between_tags(content, "tag")
    assert out == "b\nc\n"

def test_load_execute(tmp_path: Path):
    target_dir = tmp_path
    
    file1 = tmp_path / "script.py"
    file1.write_text("print('hello')\n")
    
    content = """# Main
<!-- load script.py fenced=python -->
<!-- load -->
"""
    out = Load.execute(content, str(target_dir), Action.RUN)
    expected = """# Main
<!-- load script.py fenced=python -->

```python
print('hello')
```

<!-- load -->
"""
    assert out == expected

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
    dummy_file = str(target_dir / "README.md")
    
    out = Links.execute(dummy_file, content, Action.RUN)
    expected = """# Main
<!-- links my_links -->
- [page1.md](my_links/page1.md)
- [page2.md](my_links/page2.md)
<!-- links -->
"""
    # Replace backslashes for windows compatibility in test assertion if needed, but the implementation uses replace("\\", "/")
    assert out == expected

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
