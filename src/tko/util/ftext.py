from __future__ import annotations
from typing import List,  Any, Tuple, Union


class TK:
    def __init__(self, text: str = "", fmt: str = "", ):
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        self.text = text
        self.fmt = fmt

    def __eq__(self, other: Any):
        if not isinstance(other, TK):
            return False
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
        self.data = []
        for d in data:
            for c in d.text:
                self.data.append(TK(c, d.fmt))
        return self

    def __getitem__(self, index: int) -> TK:
        if index < 0 or index >= len(self):
            raise IndexError("index out of range")
        return self.data[index]

    def __len__(self):
        return self.len()
    
    def __add__(self, other: Any):
        return FF().add(self).add(other)

    def __eq__(self, other: Any):
        if len(self.data) != len(other.data):
            return False
        for i in range(len(self.data)):
            if self.data[i] != other.data[i]:
                return False
        return True


    def __str__(self):
        return f"{"".join([str(d) for d in self.resume()])}"
    
    def resume(self) -> List[TK]:
        if len(self.data) == 0:
            return []
        
        new_data: List[TK] = [TK("", self.data[0].fmt)]
        for d in self.data:
            if d.fmt == new_data[-1].fmt:
                new_data[-1].text += d.text
            else:
                new_data.append(TK())
                new_data[-1].text = d.text
                new_data[-1].fmt = d.fmt
        return new_data
    
    def resume_val_fmt(self) -> Tuple[str, str]:
        fmt = []
        val = []
        for d in self.data:
            fmt.append(" " if d.fmt == "" else d.fmt[0])
            val.append(d.text)
        return "".join(val), "".join(fmt)


    # search for a value inside the tokens and replace it with a new value and fmt
    def replace(self, old: str, token: TK):
        old_list: List[str] = [c for c in old]
        new_list = [c for c in token.text]
        new_list.reverse()

        index = 0
        while index < len(self.data) - len(old_list) + 1:
            found = True
            for i in range(len(old_list)):
                if self.data[index + i].text != old_list[i]:
                    found = False
                    break
            if found:
                for _ in range(len(old_list)):
                    del self.data[index]
                for c in new_list:
                    self.data.insert(index, TK(c, token.fmt))
                index += len(new_list)
            else:
                index += 1
        return self

    def plus(self, qtd: int) -> FF:
        output = FF()
        for i in range(qtd):
            output.add(self)
        return output

    def add(self, value: Union[str, TK, Tuple[str, str], FF]):
        if isinstance(value, str):
            if value != "":
                for c in value:
                    self.data.append(TK(c))
        elif isinstance(value, TK):
            if value.text != "":
                for c in value.text:
                    self.data.append(TK(c, value.fmt))
        elif isinstance(value, FF):
            self.data += value.data
        else:
            raise TypeError("unsupported type '{}'".format(type(value)))
        return self
    
    def addf(self, fmt: str, text: Any):
        if not isinstance(text, str):
            raise TypeError("fmt must be a string")
        self.add(TK(text, fmt))
        return self

    def ljust(self, width: int, filler: TK = TK(" ")):
        total = self.len()
        char = " " if filler.text == "" else filler.text[0]
        fmt = filler.fmt
        if total < width:
            suffix = [TK(char, fmt) for _ in range(width - total)]
            self.data = self.data + suffix
        return self
    
    def rjust(self, width: int, filler: TK = TK(" ")):
        total = self.len()
        char = " " if filler.text == "" else filler.text[0]
        fmt = filler.fmt
        if total < width:
            prefix = [TK(char, fmt) for _ in range(width - total)]
            self.data = prefix + self.data
        return self
    
    def center(self, width: int, filler: TK):
        total = self.len()
        char = " " if filler.text == "" else filler.text[0]
        fmt = filler.fmt
        if total < width:
            left = (width - total) // 2
            right = width - total - left
            prefix = [TK(char, fmt) for _ in range(left)]
            suffix = [TK(char, fmt) for _ in range(right)]
            self.data = prefix + self.data + suffix
        return self
    
    def len(self):
        return len(self.data)
    
    def get_data(self):
        return self.data
    
    def get_text(self) -> str:
        return "".join([t.text for t in self.data])

    def trim_alfa(self, limit: int):
        return self
    
    def trim_spaces(self, limit: int):            
        return self

    def trim_end(self, width: int):
        if self.len() > width:
            self.data = self.data[:width]
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