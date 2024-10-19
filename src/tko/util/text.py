from __future__ import annotations
from typing import List,  Any, Tuple, Union

class AnsiColor:
    enabled = True
    terminal_styles = {
        '.': '\033[0m', # Reset
        '*': '\033[1m', # Bold
        '/': '\033[3m', # Italic
        '_': '\033[4m', # Underline
        
        'k': '\033[30m', # Black
        'r': '\033[31m', # Red
        'g': '\033[32m', # Green
        'y': '\033[33m', # Yellow
        'b': '\033[34m', # Blue
        'm': '\033[35m', # Magenta
        'c': '\033[36m', # Cyan
        'w': '\033[37m', # White


        'K': '\033[40m', # Background black
        'W': '\033[47m', # Background white
        "R": '\033[41m', # Background red
        "G": '\033[42m', # Background green
        "Y": '\033[43m', # Background yellow
        "B": '\033[44m', # Background blue
        "M": '\033[45m', # Background magenta
        "C": '\033[46m', # Background cyan
    }

    @staticmethod
    def colour(modifiers: str, text: str) -> str:
        if not AnsiColor.enabled:
            return text
        output = ''
        for m in modifiers:
            val = AnsiColor.terminal_styles.get(m, '')
            if val != '':
                output += val
        output += text
        if len(modifiers) > 0:
            output += AnsiColor.terminal_styles.get('.', "")
        return output

class Token:
    def __init__(self, text: str = "", fmt: str = "", ):
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        self.text = text
        self.fmt = fmt

    def __eq__(self, other: Any):
        if not isinstance(other, Token):
            return False
        return self.text == other.text and self.fmt == other.fmt

    def __len__(self):
        return len(self.text)
    
    def __add__(self, other: Any):
        return Text().add(self).add(other)

    def __str__(self):
        return f"({self.fmt}:{self.text})"

def RToken(fmt: str, text: str) -> Token:
    return Token(text, fmt)

class Text:
    def __init__(self, value: str = "", *args):
        if not isinstance(value, str):
            raise TypeError("value must be a string")
        self.data: List[Token] = []
        if value != "": 
            self.__process_placeholders(value, *args)
    
    def set_background(self, fmt: str):
        for d in self.data:
            lower_only = "".join([c for c in d.fmt if c.islower()])
            d.fmt = fmt + lower_only
        return self

    def clone(self):
        other = Text()
        other.data = [v for v in self.data]
        return other

    def setup(self, data: List[Token]):
        self.data = []
        for d in data:
            for c in d.text:
                self.data.append(Token(c, d.fmt))
        return self

    def split(self, sep: str) -> List[Text]:
        output = []
        current = Text()
        for d in self.data:
            if d.text == sep:
                output.append(current)
                current = Text()
            else:
                current.add(d)
        output.append(current)
        return output

    def slice(self, start: int | None = None, end: int | None = None) -> Text:
        if start is None:
            start = 0
        while start < 0:
            start = len(self) + start
        if end is None:
            end = len(self)
        while end < 0:
            end = len(self) + end
        output = Text()
        for i in range(start, end):
            output.add(self[i])
        return output

    def __getitem__(self, index: int) -> Token:
        if index < 0 or index >= len(self):
            raise IndexError("index out of range")
        return self.data[index]

    def __len__(self):
        return self.len()
    
    def __add__(self, other: Any):
        return Text().add(self).add(other)

    def __eq__(self, other: Any):
        if len(self.data) != len(other.data):
            return False
        for i in range(len(self.data)):
            if self.data[i] != other.data[i]:
                return False
        return True


    def __str__(self):
        output = ""
        for elem in self.resume():
            output += AnsiColor.colour(elem.fmt, elem.text)
        return output
    
    def resume(self) -> List[Token]:
        if len(self.data) == 0:
            return []
        
        new_data: List[Token] = [Token("", self.data[0].fmt)]
        for d in self.data:
            if d.fmt == new_data[-1].fmt:
                new_data[-1].text += d.text
            else:
                new_data.append(Token())
                new_data[-1].text = d.text
                new_data[-1].fmt = d.fmt
        return new_data

    # search for a value inside the tokens and replace it with a new value and fmt
    def replace(self, old: str, token: Token):
        index = 0
        while True:
            if index + len(old) > len(self.data):
                break
            sub = "".join([t.text for t in self.data[index:index + len(old)]])
            if sub == old:
                pre = self.data[:index]
                mid = [Token(t, token.fmt) for t in token.text]
                pos = self.data[index + len(old):]
                self.data = pre + mid + pos
                index += len(token.text)
            else:
                index += 1
        return self

    def plus(self, qtd: int) -> Text:
        output = Text()
        for i in range(qtd):
            output.add(self)
        return output

    def add(self, value: str | Token | Text | None):
        if value is None:
            return self
        if isinstance(value, str):
            if value != "":
                for c in value:
                    self.data.append(Token(c))
        elif isinstance(value, Token):
            if value.text != "":
                for c in value.text:
                    self.data.append(Token(c, value.fmt))
        elif isinstance(value, Text):
            self.data += value.data
        else:
            raise TypeError("unsupported type '{}'".format(type(value)))
        return self
    
    def addf(self, fmt: str, value: str | Token | Text | None):
        if isinstance(value, str):
            self.add(Token(value, fmt))
        elif isinstance(value, Token):
            self.add(Token(value.text, fmt))
        elif isinstance(value, Text):
            self.add(Token(value.get_text(), fmt))
        return self

    def ljust(self, width: int, filler: Token = Token(" ")):
        total = self.len()
        char = " " if filler.text == "" else filler.text[0]
        fmt = filler.fmt
        if total < width:
            suffix = [Token(char, fmt) for _ in range(width - total)]
            self.data = self.data + suffix
        return self
    
    def rjust(self, width: int, filler: Token = Token(" ")):
        total = self.len()
        char = " " if filler.text == "" else filler.text[0]
        fmt = filler.fmt
        if total < width:
            prefix = [Token(char, fmt) for _ in range(width - total)]
            self.data = prefix + self.data
        return self
    
    def center(self, width: int, filler: Token | str  = " "):
        if isinstance(filler, str):
            filler = Token(filler)
        total = self.len()
        char = " " if filler.text == "" else filler.text[0]
        fmt = filler.fmt
        if total < width:
            left = (width - total) // 2
            right = width - total - left
            prefix = [Token(char, fmt) for _ in range(left)]
            suffix = [Token(char, fmt) for _ in range(right)]
            self.data = prefix + self.data + suffix
        return self

    def fold_in(
        self, width: int, sep: str | Token = " ", left_border: str | Token = " ", right_border: str | Token  = " "
    ) -> Text:
        if isinstance(sep, str):
            sep = Token(sep)
        if isinstance(left_border, str):
            left_border = Token(left_border)
        if isinstance(right_border, str):
            right_border = Token(right_border)

        available = width - len(left_border) - len(right_border)
        if self.len() > available:
            self.trim_end(available)
            return Text() + left_border + self + right_border
        missing = width - self.len() - 2
        left = missing // 2
        right = missing - left
        filler_left = Text().add(sep).plus(left)
        filler_right = Text().add(sep).plus(right)
        return Text() + left_border + filler_left + self + filler_right + right_border
    
    def len(self):
        return len(self.data)
    
    def get_data(self):
        return self.data
    
    def get_text(self) -> str:
        return "".join([t.text for t in self.data])

    def cut_begin(self, qtd: int):
        if qtd > len(self.data):
            self.data = []
        else:
            self.data = self.data[qtd:]
        return self

    def trim_spaces(self, limit: int):
        return self

    def trim_end(self, width: int):
        if self.len() > width:
            self.data = self.data[:width]
        return self

    def join(self, array: List[Text]):
        out = Text()
        for i, a in enumerate(array):
            if i != 0:
                out.add(self)
            out.add(a)
        return out

    @staticmethod
    def __preprocess(data):
        # Primeira etapa: substitui << por \a
        result1 = []
        i = 0
        while i < len(data):
            if i < len(data) - 1 and data[i] == '{' and data[i + 1] == '{':
                result1.append('\a')  # Usa o marcador \a para << 
                i += 2  # Pula o próximo '<'
            else:
                result1.append(data[i])
                i += 1

        # Segunda etapa: substitui >> por \b, de trás para frente
        result2 = []
        i = len(result1) - 1
        while i >= 0:
            if i > 0 and result1[i] == '}' and result1[i - 1] == '}':
                result2.append('\b')  # Usa o marcador \b para >>
                i -= 2  # Pula o próximo '>'
            else:
                result2.append(result1[i])
                i -= 1

        # Inverter result2 para obter o resultado final
        final_result = ''.join(result2[::-1])
        return final_result

    @staticmethod
    def __extract(data):
        data = Text.__preprocess(data)  # Preprocessar a string
        texts: list[str] = [""]
        placeholders: list[str] = []
        destiny = texts  # Começa preenchendo textos"

        for c in data:
            if c == '{':
                placeholders.append("")  # Inicia um novo placeholder
                destiny = placeholders  # Muda o destino para placeholders
            elif c == '}':
                texts.append("")  # Volta para o texto
                destiny = texts
            else:
                # Substitui \a e \b por < e >
                if c == '\a':
                    c = '{'
                elif c == '\b':
                    c = '}'
                # Adiciona o caractere ao destino atual
                destiny[-1] += c

        # Garantir que o tamanho dos textos e placeholders sejam iguais
        while len(texts) > len(placeholders):
            placeholders.append("")

        return texts, placeholders

    def __process_placeholders(self, text, *args) -> None:
        params = list(args)
        texts, placeholders = Text.__extract(text)
        while len(params) < len(placeholders):
            params.append("")
        # Aplicar a função fn aos placeholders e montar o resultado final
        for i in range(len(texts)):
            value = texts[i]
            self.add(value)
            
            fmt = placeholders[i]
            value = params[i]
            if fmt == "":
                self.add(value)
            else:
                self.addf(fmt, value)

if __name__ == "__main__":
    # print(Text("comida {c:gelada}"))
    # print(Text("comida {c:gelada} e {r:quente}"))
    print(Text("a {b} está com {}", "agua", Text("{g}", "capim")))
    
