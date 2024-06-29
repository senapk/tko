from typing import List, Tuple

class Sentence:
    def __init__(self):
        self.data: List[Tuple[str, str]] = []
    
    def addf(self, fmt: str, text: str):
        self.data.append((fmt, text))
        return self
    
    def addt(self, text: str):
        self.data.append(("", text))
        return self

    def adds(self, fmt, sentence):
        for f, t in sentence.data:
            self.data.append((fmt, t))
        return self
    
    def concat(self, sentence):
        self.data += sentence.data
        return self
    
    def len(self):
        total = 0
        for _, text in self.data:
            total += len(text)
        return total
    
    def get(self):
        return self.data
