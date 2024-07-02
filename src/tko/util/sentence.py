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
            self.addt(fillchar * (width - total))
        return self
    
    def rjust(self, width: int, fillchar: str = " ", fmt = ""):
        total = self.len()
        if total < width:
            self.data = [Token("", fillchar * (width - total))] + self.data
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

    def trim_labels(self, limit: int):
        for i in range(len(self.data) - 1, -1, -1):
            token = self.data[i]
            if self.len() >= limit:
                text = token.text
                label = None
                try:
                    if "[" in text:
                        label, value = text.split("[")
                        value = "[" + value
                    elif "(" in text:
                        label, value = text.split("(")
                        value = "(" + value

                    if label:
                        if self.len() - len(label) < limit:
                            token.text = token.text[:limit - (self.len() - len(label))] + value
                        else:
                            token.text = value
                except:
                    raise Exception(f"Erro ao processar label: {text}")

    def trim_spaces(self, limit: int):
        for i in range(len(self.data) - 1, -1, -1):
            token = self.data[i]
            if self.len() >= limit:
                if token.text == " ":
                    del self.data[i]

    def cut_end(self, width: int):
        total = self.len()
        while total > width:
            last = self.data[-1]
            if len(last.text) == 0:
                self.data.pop()
            else:
                last.text = last.text[:-1]
                total -= 1
        return self