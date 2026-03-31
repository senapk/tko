from tko.util.text import Text

class TreeItem():

    def __init__(self):
        self.__remote_name: str = ""
        self.__key: str = ""
        self._title: str = ""

        self.ligature: Text = Text(" ")
        self.visible: bool = False
        self.is_requirement_color: str = ""

    def get_remote_name(self) -> str:
        return self.__remote_name

    def get_full_key(self) -> str:
        return self.__remote_name + "@" + self.__key
    
    def get_key(self) -> str:
        return self.__key
    
    def get_title(self) -> str:
        return self._title
    
    # def get_sentence(self) -> Text:
    #     return self.__sentence

    def set_remote_name(self, remote_name: str):
        self.__remote_name = remote_name
        return self
    
    def set_key(self, key: str):
        if key.startswith("@"):
            key = key[1:]
        self.__key = key
        return self

    def set_title(self, title: str):
        self._title = title
        return self
    
    def set_sentence(self, sentence: Text):
        self.__sentence = sentence
        return self
