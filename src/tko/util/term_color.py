from .text import Text
from typing import Union

class TermColor:
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
    }

def _colour(modifiers: str, text: str) -> str:
    if not TermColor.enabled:
        return text
    output = ''
    for m in modifiers:
        val = TermColor.terminal_styles.get(m, '')
        if val != '':
            output += val
    output += text
    if len(modifiers) > 0:
        output += TermColor.terminal_styles.get('.', "")
    return output

def term_colour(ftext: Text) -> str:
    output = ""
    for elem in ftext.resume():
        output += _colour(elem.fmt, elem.text)
    return output

def term_print(ftext: Union[str, Text], **kwargs):
    if isinstance(ftext, str):
        print(ftext, **kwargs)
    else:
        print(ftext, **kwargs)