from __future__ import annotations
from typing import List,  Any, Tuple, Union


class Token:
    def __init__(self, fmt: str = "", text: str = ""):
        self.fmt = fmt
        self.text = text

    def __eq__(self, other: Token):
        return self.text == other.text and self.fmt == other.fmt

    def __len__(self):
        return len(self.text)
    
    def __add__(self, other: Any):
        return Ftext().add(self).add(other)

    def __str__(self):
        return f"({self.fmt}:{self.text})"

class Ftext:
    def __init__(self, value: Union[str, Tuple[str, str]] = ""):
        self.data: List[Token] = []
        self.add(value)
    
    def __getitem__(self, index: int):
        return self.data[index]
    
    def __setitem__(self, index: int, value: Token):
        self.data[index] = value
        return None
    
    def __len__(self):
        return self.len()
    
    def __add__(self, other: Any):
        return Ftext().add(self).add(other)

    def __eq__(self, other: Ftext):
        if len(self.data) != len(other.data):
            return False
        for i in range(len(self.data)):
            if self.data[i] != other.data[i]:
                return False
        return True

    def __str__(self):
        return "".join([str(t) for t in self.data])

    def add(self, value: Union[str, Token, Tuple[str, str], Ftext]):
        if isinstance(value, str):
            if value != "":
                self.data.append(Token("", value))
        elif isinstance(value, Token):
            if value.text != "":
                self.data.append(value)
        elif isinstance(value, Tuple):
            fmt, text = value
            if text != "":
                self.data.append(Token(fmt, text))
        elif isinstance(value, Ftext):
            self.data += value.data
        else:
            raise TypeError("unsupported type '{}'".format(type(value)))
        return self
    
    def addf(self, fmt: str, text: str):
        self.add(Token(fmt, text))
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
    
    def get(self):
        return self.data

    def trim_alfa(self, limit: int):
        if limit < 0:
            return self
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
        return self

    def trim_spaces(self, limit: int):
        if limit < 0:
            return self
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
            
        return self

    def trim_end(self, width: int):
        if width < 0:
            return self
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
        return self

    @staticmethod
    def build_bar(text: str, percent: float, length: int, fmt_true: str = "/kC",
                  fmt_false: str = "/kY") -> Ftext:
        prefix = (length - len(text)) // 2
        suffix = length - len(text) - prefix
        text = " " * prefix + text + " " * suffix
        total = length
        full_line = text
        done_len = int(percent * total)
        xp_bar = Ftext() + (fmt_true, full_line[:done_len]) + (fmt_false, full_line[done_len:])
        return xp_bar