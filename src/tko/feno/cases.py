from pathlib import Path
import subprocess

class Cases:

    @staticmethod
    def run(cases_file: Path, source_readme: Path, source_dir: Path) -> None:
        # Encontra recursivamente arquivos de casos, sem tratar configurações
        # de feedback como testes.
        files: list[Path] = sorted(
            (
                path
                for path in source_dir.rglob("*")
                if path.is_file()
                and path.suffix in {".tio", ".vpl", ".cases", ".toml"}
                and path.name != "feedback.toml"
            ),
            key=lambda path: path.as_posix(),
        )

        # evita shell=True e mantém tipagem correta
        cmd: list[str] = ["tko", "build", "tests", str(cases_file), str(source_readme)] + [str(f) for f in files]

        subprocess.run(cmd, stdout=subprocess.PIPE, check=False)
