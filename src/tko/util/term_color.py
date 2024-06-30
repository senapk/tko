class Color:
    enabled = False
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

    @staticmethod
    def ljust(text: str, width: int) -> str:
        return text + " " * (width - Color.len(text))

    @staticmethod
    def center(text: str, width: int, filler: str) -> str:
        before = filler * ((width - Color.len(text)) // 2)
        after = filler * ((width - Color.len(text) + 1) // 2)
        return before + text + after

    @staticmethod
    def remove_colors(text: str) -> str:
        for color in Color.terminal_styles.values():
            text = text.replace(color, "")
        return text

    @staticmethod
    def len(text):
        return len(Color.remove_colors(text))


def colour(modifiers: str, text: str) -> str:
    if not Color.enabled:
        return text
    
    output = ''
    for m in modifiers:
        val = Color.terminal_styles.get(m, '')
        if val != '':
            output += val
    output += text + Color.terminal_styles.get('.', "")
    return output


