# ignore missing import 
from typing import Any
import chardet
import os

class Decoder:

    @staticmethod
    def load(file_path: str) -> str:
        if not os.path.exists(file_path):

            raise Exception("Arquivo {} não encontrado".format(os.path.abspath(file_path)))
        with open(file_path, "rb") as file:
            raw_data = file.read()
            enc_dict: dict[str, Any] = chardet.detect(raw_data) # type: ignore
            encoding: str = enc_dict["encoding"] or "utf-8" # type: ignore
            if enc_dict["confidence"] < 0.90:
                encoding = "utf-8"
            try:
                content = raw_data.decode(encoding)  # type: ignore
            except UnicodeDecodeError as _:
                content = raw_data.decode(enc_dict["encoding"] or "utf-8") # type: ignore
            return content.replace('\r\n', '\n')

    @staticmethod
    def save(file_path: str, content: str):
        base_path = os.path.dirname(file_path)
        if base_path != "" and not os.path.exists(base_path):
            os.makedirs(base_path)
        with open(file_path, "w", encoding="utf-8", newline='\n') as file:
            file.write(content)

    @staticmethod
    def get_encoding(file_path: str) -> str:
        with open(file_path, "rb") as file:
            raw_data = file.read()
            enc_dict = chardet.detect(raw_data)
            encoding = enc_dict["encoding"]
            if enc_dict["confidence"] < 0.90:
                encoding = "utf-8"
            return encoding or "utf-8"