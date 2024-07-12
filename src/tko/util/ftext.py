from __future__ import annotations
from typing import List,  Any, Tuple, Union


class TK:
    def __init__(self, text: str = "", fmt: str = "", ):
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        self.text = text
        self.fmt = fmt

    def __eq__(self, other: TK):
        return self.text == other.text and self.fmt == other.fmt

    def __len__(self):
        return len(self.text)
    
    def __add__(self, other: Any):
        return FF().add(self).add(other)

    def __str__(self):
        return f"('{self.text}', '{self.fmt}')"

def TR(fmt: str, text: str) -> TK:
    return TK(text, fmt)

class FF:
    def __init__(self, value: Union[str, Tuple[str, str]] = ""):
        self.data: List[TK] = []
        self.add(value)
    
    def setup(self, data: List[TK]):
        self.data = data
        return self

    def __getitem__(self, index: int) -> TK:
        if index < 0 or index >= len(self):
            return TK()
        return self.separate().data[index]

    def __len__(self):
        return sum([len(t.text) for t in self.data])
    
    def __add__(self, other: Any):
        return FF().add(self).add(other)

    def __eq__(self, other: FF):
        if len(self.data) != len(other.data):
            return False
        for i in range(len(self.data)):
            if self.data[i] != other.data[i]:
                return False
        return True


    def __str__(self):
        return "".join([str(t) for t in self.data])
    
    def separate(self):
        out = FF()
        for d in self.data:
            for c in d.text:
                out.add(TK(c, d.fmt))
        return out

    def join(self):
        if len(self.data) == 0:
            return self
        
        new_data: List[TK] = [TK("", self.data[0].fmt)]
        for d in self.data:
            if d.fmt == new_data[-1].fmt:
                new_data[-1].text += d.text
            else:
                new_data.append(TK())
                new_data[-1].text = d.text
                new_data[-1].fmt = d.fmt
        self.data = new_data

        return self

    # search for a value inside the tokens and replace it with a new value and fmt
    def replace(self, old: str, token: TK):
        if len(old) != 1:
            raise ValueError("old must be a single character")
        value = self.separate()

        for i in range(len(value.data)):
            elem = value.data[i]
            if elem.text == old:
                value.data[i] = token
        self.data = value.data
        self.join()
        return self

    def plus(self, qtd: int) -> FF:
        output = FF()
        for i in range(qtd):
            output.add(self)
        return output

    def add(self, value: Union[str, TK, Tuple[str, str], FF]):
        if isinstance(value, str):
            if value != "":
                self.data.append(TK(value))
        elif isinstance(value, TK):
            if value.text != "":
                self.data.append(value)
        elif isinstance(value, Tuple):
            text, fmt = value
            if text != "":
                self.data.append(TK(text, fmt))
        elif isinstance(value, FF):
            self.data += value.data
        else:
            raise TypeError("unsupported type '{}'".format(type(value)))
        return self
    
    def addf(self, fmt: str, text: Any):
        if not isinstance(text, str):
            raise TypeError("fmt must be a string")
        self.data.append(TK(text, fmt))
        return self

    def ljust(self, width: int, filler: TK):
        total = self.len()
        if total < width:
            self.add(TK(filler.text * (width - total), filler.fmt))
        return self
    
    def rjust(self, width: int, filler: TK):
        total = self.len()
        if total < width:
            self.data = [TK(filler.text * (width - total), filler.fmt)] + self.data
        return self
    
    def center(self, width: int, filler: TK):
        total = self.len()
        if total < width:
            left = (width - total) // 2
            right = width - total - left
            self.data = [TK(filler.text * left, filler.fmt)] + self.data + [TK(filler.text * right, filler.fmt)]
        return self
    
    def len(self):
        total = 0
        for t in self.data:
            total += len(t.text)
        return total
    
    def get_data(self):
        return self.data
    
    def get_text(self) -> str:
        return "".join([t.text for t in self.data])

    def get(self, index: int):
        return self.data[index]

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
                  fmt_false: str = "/kY") -> FF:
        prefix = (length - len(text)) // 2
        suffix = length - len(text) - prefix
        text = " " * prefix + text + " " * suffix
        total = length
        full_line = text
        done_len = int(percent * total)
        xp_bar = FF() + (full_line[:done_len], fmt_true) + (full_line[done_len:], fmt_false)
        return xp_bar