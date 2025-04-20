from tko.util.decoder import Decoder

class Title:
    @staticmethod
    def extract_title(readme_file: str) -> str:
        content = Decoder.load(readme_file)
        title = content.splitlines()[0]
        parts = title.split(" ")
        if parts[0].count("#") == len(parts[0]):
            del parts[0]
        title = " ".join(parts)
        return title