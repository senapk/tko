# ignore missing import 
import os

class Decoder:

    @staticmethod


    def load(file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().replace("\r\n", "\n")
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read().replace("\r\n", "\n")

    @staticmethod
    def save(file_path: str, content: str):
        base_path = os.path.dirname(file_path)
        if base_path != "" and not os.path.exists(base_path):
            os.makedirs(base_path)
        with open(file_path, "w", encoding="utf-8", newline='\n') as file:
            file.write(content)
