from pathlib import Path
from tko.i18n import Msg
from loguru import logger
from tko.util.console import Console



_INDEXER_REPLACE_TITLE_README_MISSING = Msg.parse(
    pt="Erro: Arquivo README '{readme}' não existe, não é possível substituir o título.",
    en="Error: README file '{readme}' does not exist, cannot replace title.",
)

_INDEXER_REPLACED_TITLE = Msg.parse(
    pt="Título em '{readme}' substituído por '{title}'",
    en="Replaced title in '{readme}' with '{title}'",
)

class IndexerMd:
    @staticmethod
    def _front_matter_end(lines: list[str]) -> int:
        if not lines or lines[0].strip() != "---":
            return 0
        for index, line in enumerate(lines[1:], 1):
            if line.strip() in {"---", "..."}:
                return index + 1
        return 0

    @staticmethod
    def load_title_from_markdown_file(path: Path) -> str | None:
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines[IndexerMd._front_matter_end(lines):]:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
        return None

    @staticmethod
    def replace_title_in_readme(readme_file: Path, new_title: str, verbose: bool) -> None:
        if not readme_file.exists():
            logger.error(str(_INDEXER_REPLACE_TITLE_README_MISSING).format(readme=readme_file))
            return
        with open(readme_file, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.splitlines(keepends=True)
        front_matter_end = IndexerMd._front_matter_end(lines)
        title_line = next(
            (
                index
                for index, line in enumerate(lines[front_matter_end:], front_matter_end)
                if line.strip().startswith("# ")
            ),
            None,
        )
        if title_line is not None:
            line = lines[title_line]
            indentation = line[: len(line) - len(line.lstrip())]
            line_ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            lines[title_line] = f"{indentation}# {new_title}{line_ending}"
        else:
            line_ending = "\r\n" if "\r\n" in content else "\n"
            lines.insert(front_matter_end, f"# {new_title}{line_ending}")
        new_content = "".join(lines)
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        if verbose:
            Console.print(str(_INDEXER_REPLACED_TITLE).format(readme=readme_file, title=new_title))
