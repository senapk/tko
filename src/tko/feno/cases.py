from pathlib import Path
import subprocess

class Cases:

    @staticmethod
    def run(cases_file: Path, source_readme: Path, source_dir: Path) -> None:
        # encontra recursivamente arquivos .tio, .vpl e .toml
        files: list[Path] = [
            p for p in source_dir.rglob("*")
            if p.is_file() and p.suffix in {".tio", ".vpl", ".toml"}
        ]

        # evita shell=True e mantém tipagem correta
        cmd: list[str] = ["tko", "build", "tests", str(cases_file), str(source_readme)] + [str(f) for f in files]

        subprocess.run(cmd, stdout=subprocess.PIPE, check=False)
