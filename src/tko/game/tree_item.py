from tko.util.text import Text

class TreeItem:
    def __init__(self):
        self.sentence = Text()
        self.key = ""
        self.title = ""

    def get_key(self):
        return self.key

    def get_title(self):
        return self.title
    
    def get_sentence(self):
        return self.sentence
