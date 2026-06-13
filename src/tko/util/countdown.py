
_BLOCKS: str = " ▁▂▃▄▅▆▇█"
_BRAILLE: str = "⠀⠁⠃⠇⠏⠟⠿⣿"

class Countdown:
    @staticmethod
    def braille(value: float, maximum: float, length: int) -> str:
        if maximum <= 0:
            raise ValueError("maximum deve ser maior que zero")

        value = max(0.0, min(value, maximum))
        value = maximum - value  # Inverter para mostrar o progresso decrescente

        units: float = (value / maximum) * length

        full: int = int(units)
        partial: int = int((units - full) * (len(_BRAILLE) - 1))

        result: list[str] = ["⣿"] * full

        if full < length:
            result.append(_BRAILLE[partial])

        while len(result) < length:
            result.append("⠀")  # braille em branco

        return "".join(result[:length])

    @staticmethod
    def countdown_bar(value: float, maximum: float, length: int) -> str:
        if maximum <= 0:
            raise ValueError("maximum deve ser maior que zero")

        value = max(0.0, min(value, maximum))

        units: float = (value / maximum) * length
        full: int = int(units)
        partial: int = int((units - full) * 8)

        result: str = "█" * full

        if full < length:
            result += _BLOCKS[partial]
            result += " " * (length - len(result))

        return result[:length]

if __name__ == "__main__":
    import time
    import sys

    total: int = 100
    for i in range(total + 1):
        bar: str = Countdown.braille(i, total, 30)
        print(f"\r[{bar}] {i}%", end="")
        sys.stdout.flush()
        time.sleep(0.1)
    print()