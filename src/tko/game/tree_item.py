from tko.util.text import Text

class TreeItem:
    def __init__(self):
        self.sentence: Text = Text()
        self.key: str = ""
        self.title: str = ""

    def get_key(self):
        return self.key

    def get_title(self):
        return self.title
    
    def get_sentence(self):
        return self.sentence
