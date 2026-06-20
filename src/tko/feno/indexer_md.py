from pathlib import Path
from tko.i18n import Msg
from loguru import logger
import re
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
    def load_title_from_markdown_file(path: Path) -> str | None:
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
        return "NÃO TEM TÍTULO"
    
    @staticmethod
    def replace_title_in_readme(readme_file: Path, new_title: str, verbose: bool) -> None:
        if not readme_file.exists():
            logger.error(str(_INDEXER_REPLACE_TITLE_README_MISSING).format(readme=readme_file))
            return
        with open(readme_file, "r", encoding="utf-8") as f:
            content = f.read()
        # regex to replace first line starting with # with the new title
        regex = r'^(# .*)$'
        new_content = re.sub(regex, f"# {new_title}", content, count=1, flags=re.MULTILINE)
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        if verbose:
            Console.print(str(_INDEXER_REPLACED_TITLE).format(readme=readme_file, title=new_title))
