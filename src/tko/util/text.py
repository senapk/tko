from __future__ import annotations
from typing import Any

import re

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



class Text:
    @staticmethod
    def r_token(fmt: str, text: str) -> Token:
        return Text.Token(text, fmt)

    class Token:
        def __init__(self, text: str = "", fmt: str = ""):
            if not isinstance(text, str): # type: ignore
                raise TypeError("text must be a string")
            self.text = text
            self.fmt = fmt

        # @override
        def __eq__(self, other: Any):
            if not isinstance(other, Text.Token):
                return False
            return self.text == other.text and self.fmt == other.fmt

        def __len__(self):
            return len(self.text)
        
        def __add__(self, other: Any):
            return Text().add(self).add(other)

        # @override
        def __str__(self):
            return f"({self.fmt}:{self.text})"
        
    def __init__(self, default_fmt: str = ""):
        self.data: list[Text.Token] = []
        self.default_fmt = default_fmt


    # convert a strings formatted with terminal styles to a Text object
    @staticmethod
    def decode_raw(data: str) -> Text:
        # Mapeamento direto de códigos ANSI para identificadores de formato
        ansi_to_format: dict[str, str] = {
            '\033[34m': 'b',  # Blue
            '\033[35m': 'm',  # Magenta
            '\033[32m': 'g',  # Green
            '\033[33m': 'y',  # Yellow
            '\033[31m': 'r',  # Red
            '\033[36m': 'c',  # Cyan
            '\033[37m': 'w',  # White
            '\033[0m': '',    # Reset
        }

        # Cria uma regex para encontrar qualquer um dos códigos ANSI
        # O re.escape garante que caracteres especiais na chave sejam tratados literalmente
        # O '|' cria uma alternância (OU)
        pattern = '|'.join(re.escape(key) for key in ansi_to_format.keys())

        text = Text()
        fmt = ""
        last_idx = 0

        # Itera sobre todas as ocorrências dos códigos ANSI
        for match in re.finditer(pattern, data):
            # Adiciona os caracteres que não são códigos ANSI
            if match.start() > last_idx:
                for char in data[last_idx:match.start()]:
                    text.add(Text.Token(char, fmt))

            # Atualiza o formato com base no código ANSI encontrado
            ansi_code = match.group(0)
            fmt = ansi_to_format[ansi_code]
            last_idx = match.end()

        # Adiciona quaisquer caracteres restantes após o último código ANSI
        if last_idx < len(data):
            for char in data[last_idx:]:
                text.add(Text.Token(char, fmt))

        return text


    @staticmethod
    def format(value: str = "", *args: Any) -> Text:
        # if not isinstance(value, str):
        #     raise TypeError("value must be a string")
        text = Text()
        text.__process_placeholders(value, *args)
        return text

    def set_background(self, fmt: str):
        for d in self.data:
            lower_only = "".join([c for c in d.fmt if c.islower()])
            d.fmt = fmt + lower_only
        return self

    def clone(self):
        other = Text()
        other.data = [v for v in self.data]
        return other

    def setup(self, data: list[Text.Token]):
        self.data = []
        for d in data:
            for c in d.text:
                self.data.append(Text.Token(c, d.fmt))
        return self

    def split(self, sep: str) -> list[Text]:
        output: list[Text] = []
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

    def __getitem__(self, index: int) -> Text.Token:
        if index < 0 or index >= len(self):
            raise IndexError("index out of range")
        return self.data[index]

    def __len__(self):
        return self.len()
    
    def __add__(self, other: Any):
        return Text(self.default_fmt).add(self).add(other)

    # @override
    def __eq__(self, other: Any):
        if len(self.data) != len(other.data):
            return False
        for i in range(len(self.data)):
            if self.data[i] != other.data[i]:
                return False
        return True

    # @override
    def __str__(self):
        return self.ansi()

    def ansi(self) -> str:
        output = ""
        for elem in self.resume():
            output += AnsiColor.colour(elem.fmt, elem.text)
        return output
    
    def resume(self) -> list[Text.Token]:
        # Group consecutive text with the same fmt
        if len(self.data) == 0:
            return []
        
        new_data: list[Text.Token] = [Text.Token("", self.data[0].fmt)]
        for d in self.data:
            if d.fmt == new_data[-1].fmt:
                new_data[-1].text += d.text
            else:
                new_data.append(Text.Token())
                new_data[-1].text = d.text
                new_data[-1].fmt = d.fmt
        return new_data

    # search for a value inside the tokens and replace it with a new value and fmt
    def replace(self, old: str, token: Text.Token):
        index = 0
        while True:
            if index + len(old) > len(self.data):
                break
            sub = "".join([t.text for t in self.data[index:index + len(old)]])
            if sub == old:
                pre = self.data[:index]
                mid = [Text.Token(t, token.fmt) for t in token.text]
                pos = self.data[index + len(old):]
                self.data = pre + mid + pos
                index += len(token.text)
            else:
                index += 1
        return self

    def repeat(self, qtd: int) -> Text:
        output = Text()
        for _ in range(qtd):
            output.add(self)
        return output

    def add(self, value: str | Text.Token | Text | tuple[str, str] | None):
        if value is None:
            return self
        if isinstance(value, str):
            if value != "":
                for c in value:
                    self.data.append(Text.Token(c, self.default_fmt))
        elif isinstance(value, Text.Token):
            if value.text != "":
                for c in value.text:
                    self.data.append(Text.Token(c, value.fmt))
        elif isinstance(value, Text):  # type: ignore
            self.default_fmt = value.default_fmt
            self.data += [x for x in value.data]
        else:
            raise TypeError("unsupported type '{}'".format(type(value)))
        return self
    
    def addf(self, fmt: str, value: str | Text.Token | Text | None):
        if isinstance(value, str):
            self.add(Text.Token(value, fmt))
        elif isinstance(value, Text.Token):
            self.add(Text.Token(value.text, fmt))
        elif isinstance(value, Text):
            self.add(Text.Token(value.get_str(), fmt))
        return self

    def ljust(self, width: int, filler: Text.Token = Token(" ")):
        total = self.len()
        char = " " if filler.text == "" else filler.text[0]
        fmt = filler.fmt
        if total < width:
            suffix = [Text.Token(char, fmt) for _ in range(width - total)]
            self.data = self.data + suffix
        return self
    
    def rjust(self, width: int, filler: Text.Token = Token(" ")):
        total = self.len()
        char = " " if filler.text == "" else filler.text[0]
        fmt = filler.fmt
        if total < width:
            prefix = [Text.Token(char, fmt) for _ in range(width - total)]
            self.data = prefix + self.data
        return self
    
    def center(self, width: int, filler: Token = Token(" ")):
        if isinstance(filler, str):
            filler = Text.Token(filler)
        total = self.len()
        char = " " if filler.text == "" else filler.text[0]
        fmt = filler.fmt
        if total < width:
            left = (width - total) // 2
            right = width - total - left
            prefix = [Text.Token(char, fmt) for _ in range(left)]
            suffix = [Text.Token(char, fmt) for _ in range(right)]
            self.data = prefix + self.data + suffix
        return self

    def fold_in(
        self, width: int, sep: str | Text.Token = " ", left_border: str | Text.Token = " ", right_border: str | Text.Token  = " "
    ) -> Text:
        if isinstance(sep, str):
            sep = Text.Token(sep)
        if isinstance(left_border, str):
            left_border = Text.Token(left_border)
        if isinstance(right_border, str):
            right_border = Text.Token(right_border)

        available = width - len(left_border) - len(right_border)
        if self.len() > available:
            self.trim_end(available)
            return Text() + left_border + self + right_border
        missing = width - self.len() - 2
        left = missing // 2
        right = missing - left
        filler_left = Text().add(sep).repeat(left)
        filler_right = Text().add(sep).repeat(right)
        return Text() + left_border + filler_left + self + filler_right + right_border
    
    def len(self):
        return len(self.data)
    
    def get_data(self):
        return self.data
    
    def get_str(self) -> str:
        return "".join([t.text for t in self.data])

    def cut_begin(self, qtd: int):
        if qtd > len(self.data):
            self.data = []
        else:
            self.data = self.data[qtd:]
        return self

    def trim_end(self, width: int):
        if self.len() > width:
            self.data = self.data[:width]
        return self

    def join(self, array: list[Text]):
        out = Text()
        for i, a in enumerate(array):
            if i != 0:
                out.add(self)
            out.add(a)
        return out

    @staticmethod
    def __preprocess(data: str):
        # Primeira etapa: substitui << por \a
        result1: list[str] = []
        i = 0
        while i < len(data):
            if i < len(data) - 1 and data[i] == '{' and data[i + 1] == '{':
                result1.append('\a')  # Usa o marcador \a para << 
                i += 2  # Pula o próximo '<'
            else:
                result1.append(data[i])
                i += 1

        # Segunda etapa: substitui >> por \b, de trás para frente
        result2: list[str] = []
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
    def __extract(data: str) -> list[tuple[str, str]]:
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
                # Substitui \a e \b por { e }
                if c == '\a':
                    c = '{'
                elif c == '\b':
                    c = '}'
                # Adiciona o caractere ao destino atual
                destiny[-1] += c

        # Garantir que o tamanho dos textos e placeholders sejam iguais
        while len(texts) > len(placeholders):
            placeholders.append("")

        return list(zip(texts, placeholders))

    @staticmethod
    def __process_fmt(fmt: str) -> tuple[str, str]:
        if fmt == "":
            return "", ""
        if ":" in fmt:
            parts: list[str] = fmt.split(":")
            if len(parts) > 1:
                return parts[0], ":".join(parts[1:])
            if len(parts) == 1:
                return parts[0], ""
        return fmt, ""

    def __process_placeholders(self, text: str, *args: Any) -> None:
        params: list[str | Text | Text.Token] = list(args)
        for text_data, placeholder in Text.__extract(text):
            self.add(text_data)
            fmt, data = Text.__process_fmt(placeholder)
            if data == "" and len(params) > 0:
                data = params[0]
                params = params[1:]
            if fmt == "":
                self.add(data)
            else:
                self.addf(fmt, data)
        for elem in params:
            self.add(elem)

    

if __name__ == "__main__":
    # Formatação usando placeholders {} e argumentos variádicos
    # Cor de conteúdo no texto
    print(Text.format("O Brasil é {b:azul}, {g:verde} e {y:amarelo}"))
    # Cor no texto e conteúdo nos argumentos
    print(Text.format("O Brasil é {b}, {g} e {y}.", "azul", "verde", "amarelo"))
    # Carrega tupla, ou conteúdo ou nada
    print(Text.format("O Brasil é {}, {g:verde} e {y}.", ("b", "azul"), "amarelo"))

    # Funciona também por adição
    print(Text() + "O Brasil é " + Text.r_token("b", "azul") + ", " + Text.r_token("g", "verde") + " e " + Text.r_token("y", "amarelo"))
    # Dá pra definir a formatação padrão para quando não for passado nada
    print(Text("r") + "O Brasil é " + Text.r_token("b", "azul") + ", " + Text.r_token("g", "verde") + " e " + Text.r_token("y", "amarelo"))
    # A formatação pode incluir cores de fundo
    print(Text("Yw") + "O Brasil é " + Text.r_token("Rb", "azul") + ", " + Text.r_token("Kg", "verde") + " e " + Text.r_token("y", "amarelo"))

    # Dá pra concatenar, somar ou passar por parâmetro
    print(Text("R") + "Tudo em vermelho " + Text("G") + " e tudo em verde")