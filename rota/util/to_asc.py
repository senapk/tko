import unicodedata

def uni_to_asc(input_str: str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

class SearchAsc:
    def __init__(self, pattern: str):
        self.pattern = uni_to_asc(pattern.lower())

    def find(self, title: str) -> int:
        return uni_to_asc(title.lower()).find(self.pattern)
    
    def inside(self, title: str) -> bool:
        return self.find(title) != -1