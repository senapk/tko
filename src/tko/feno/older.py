from typing import Tuple
from pathlib import Path

class Older:
    # return the last update for the most recent file in the directory
    @staticmethod
    def last_update(path: Path) -> Tuple[Path, float]:
        if path.is_file():
            return path, path.stat().st_mtime

        # percorre recursivamente usando pathlib
        arquivos: list[Path] = [p for p in path.rglob("*") if p.is_file()]

        if not arquivos:
            return path, path.stat().st_mtime

        # pega o mais recente
        mais_recente: Path = max(arquivos, key=lambda p: p.stat().st_mtime)
        return mais_recente, mais_recente.stat().st_mtime

    # busca recursivamente o arquivo mais recente dentro os arquivos passados

    @staticmethod
    def find_older(targets: list[Path]) -> Path:
        return max((Older.last_update(t) for t in targets), key=lambda x: x[1])[0]
