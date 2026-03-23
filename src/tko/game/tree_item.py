from tko.util.text import Text

class TreeItem():

    def __init__(self):
        self.__alias: str = ""
        self.__key: str = ""
        self._title: str = ""
        self.__sentence: Text = Text()

    def get_alias(self) -> str:
        return self.__alias

    def get_db_key(self) -> str:
        return self.__alias + "@" + self.__key
    
    def get_key_only(self) -> str:
        return self.__key
    
    def get_title(self) -> str:
        return self._title
    
    def get_sentence(self) -> Text:
        return self.__sentence

    def set_alias(self, alias: str):
        self.__alias = alias
        return self
    
    def set_key(self, key: str):
        self.__key = key
        return self

    def set_title(self, title: str):
        self._title = title
        return self
    
    def set_sentence(self, sentence: Text):
        self.__sentence = sentence
        return self
