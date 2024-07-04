from __future__ import annotations
from typing import List, Tuple


class Token:
    def __init__(self, fmt: str, text: str):
        self.fmt = fmt
        self.text = text
    
    def __len__(self):
        return len(self.text)

class Sentence:
    def __init__(self):
        self.data: List[Token] = []
    
    def addf(self, fmt: str, text: str):
        self.data.append(Token(fmt, text))
        return self
    
    def addt(self, text: str):
        self.data.append(Token("", text))
        return self
    
    def __getitem__(self, index: int):
        return self.data[index]
    
    def __setitem__(self, index: int, value: Token):
        self.data[index] = value
        return None

    def adds(self, fmt, sentence):
        for _, t in sentence.data:
            self.data.append(Token(fmt, t))
        return self
    
    def concat(self, sentence: Sentence):
        self.data += sentence.data
        return self
    
    def ljust(self, width: int, fillchar: str = " ", fmt = ""):
        total = self.len()
        if total < width:
            self.addf(fmt, fillchar * (width - total))
        return self
    
    def rjust(self, width: int, fillchar: str = " ", fmt = ""):
        total = self.len()
        if total < width:
            self.data = [Token(fmt, fillchar * (width - total))] + self.data
        return self
    
    def center(self, width: int, fillchar: str = " ", fmt = ""):
        total = self.len()
        if total < width:
            left = (width - total) // 2
            right = width - total - left
            self.data = [Token(fmt, fillchar * left)] + self.data + [Token(fmt, fillchar * right)]
        return self
    
    def len(self):
        total = 0
        for t in self.data:
            total += len(t.text)
        return total
    
    def __len__(self):
        return self.len()
    
    def get(self):
        return self.data

    def trim_alfa(self, limit: int):
        if limit < 0:
            return
        index = len(self.data) - 1
        size = self.len()
        while True:
            if index < 0 or size <= limit:
                break
            token = self.data[index]
            if len(token.text) == 0:
                del self.data[index]
                index -= 1
            elif token.text[-1].isalpha():
                token.text = token.text[:-1]
                size -= 1
            else:
                index -= 1

    def trim_spaces(self, limit: int):
        if limit < 0:
            return
        index = len(self.data) - 1
        size = self.len()
        while True:
            if index < 0 or size <= limit:
                break
            token = self.data[index]
            if len(token.text) == 0:
                del self.data[index]
                index -= 1
            elif token.text[-1] == " ":
                token.text = token.text[:-1]
                size -= 1
            else:
                index -= 1

    def trim_end(self, width: int):
        if width < 0:
            return
        size = self.len()
        index = len(self.data) - 1
        while True:
            if size <= width or index < 0:
                break
            token = self.data[index]
            if len(token.text) == 0:
                del self.data[index]
                index -= 1
            else:
                token.text = token.text[:-1]
                size -= 1
