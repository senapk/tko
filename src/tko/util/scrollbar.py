from dataclasses import dataclass

@dataclass
class ScrollBar:
    text_size: int        # tamanho total do conteúdo
    index: int            # posição atual (topo da tela)
    screen_size: int      # tamanho da área visível
    bar_size: int = 40    # tamanho total da barra
    min_block_size: int = 1  # tamanho mínimo do scroll
    char_block: str = "#"  # caractere para o bloco de scroll
    char_empty: str = "-"  # caractere para o espaço vazio

    def render(self) -> str:
        before, block_size, after = self.count_before_inside_after()
        return f"{self.char_empty * before}{self.char_block * block_size}{self.char_empty * after}"
    
    def count_before_inside_after(self) -> tuple[int, int, int]:
        if self.text_size <= self.screen_size or self.text_size == 0:
            return (0, 0, self.bar_size)

        max_index: int = self.text_size - self.screen_size
        index: int = max(0, min(self.index, max_index))

        visible_ratio: float = self.screen_size / self.text_size
        block_size: int = round(self.bar_size * visible_ratio)
        block_size = max(self.min_block_size, min(self.bar_size, block_size))

        position_ratio: float = index / max_index if max_index > 0 else 0.0
        before: int = round((self.bar_size - block_size) * position_ratio)
        after: int = self.bar_size - before - block_size

        return (before, block_size, after)

if __name__ == "__main__":
    sb = ScrollBar(text_size=20, index=0, screen_size=30, bar_size=90)
    print(f"{sb.render()}")
    before, inside, after = sb.count_before_inside_after()
    empty = "-"
    block = "#"
    print(f"{empty * before}{block * inside}{empty * after}")
