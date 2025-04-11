import os
from tko.util.decoder import Decoder

class FenoTitle:
    @staticmethod
    def extract_title(readme_file):

        folder = os.path.basename(os.path.dirname(readme_file))

        title = Decoder.load(readme_file).splitlines()[0]
        parts = title.split(" ")
        if parts[0].count("#") == len(parts[0]):
            del parts[0]
        title = " ".join(parts)
        return "@" + folder + ": " + title