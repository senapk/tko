from pathlib import Path
import unicodedata

class Decoder:

    @staticmethod


    def load(file_path: str | Path, normalize_endl: bool = True) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                value = f.read().replace("\r\n", "\n")
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                value = f.read().replace("\r\n", "\n")
        value =  unicodedata.normalize("NFC", value)
        if normalize_endl and value != "" and value[-1] != "\n":
            return value + "\n"
        return value

    @staticmethod
    def save(file_path: str | Path, content: str):
        file_path = Path(file_path)
        base_path = file_path.parent
        base_path.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8", newline='\n') as file:
            file.write(content)
