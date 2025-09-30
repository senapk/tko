from tko.util.text import Text
from tko.settings.legacy import Legacy

class TreeItem():

    def __init__(self):
        self.__database: str = ""
        self.__key: str = ""
        self._title: str = ""
        self.__sentence: Text = Text()

    def get_database(self) -> str:
        return self.__database

    def get_db_key(self) -> str:
        if self.__database == Legacy.LEGACY_DATABASE:
            return self.__key
        return self.__database + "@" + self.__key
    
    def get_only_key(self) -> str:
        return self.__key
    
    def get_title(self) -> str:
        return self._title
    
    def get_sentence(self) -> Text:
        return self.__sentence

    def set_database(self, database: str):
        self.__database = database
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
