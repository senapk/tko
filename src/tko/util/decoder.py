from pathlib import Path

class Decoder:

    @staticmethod


    def load(file_path: str | Path) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().replace("\r\n", "\n")
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read().replace("\r\n", "\n")

    @staticmethod
    def save(file_path: str | Path, content: str):
        file_path = Path(file_path)
        base_path = file_path.parent
        base_path.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8", newline='\n') as file:
            file.write(content)
