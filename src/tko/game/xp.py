from tko.game.game import Game

class XP:
    token_level_one = "level_one"
    token_level_mult = "level_mult"
    level_one: int = 100
    level_mult: float = 1.5
    
    def __init__(self, game: Game):
        self.game = game
        self.obtained = 0
        self.avaliable = 0
        self.update()
        self.level = self.get_level()
    
    def update(self):
        self.obtained, self.avaliable = self.game.get_xp_resume()

    def get_level(self) -> int:
        return self.calc_level(self.obtained)

    def get_xp_level_current(self) -> int:
        xp_prev = self.calc_xp(self.level)
        atual = self.obtained - xp_prev
        return atual

    def get_xp_level_needed(self) -> int:
        xp_next = self.calc_xp(self.level + 1)
        xp_prev = self.calc_xp(self.level)
        return xp_next - xp_prev

    def get_xp_total_obtained(self) -> int:
        return self.obtained

    def get_xp_total_available(self) -> int:
        return self.avaliable

    def calc_level(self, xp: int) -> int:
        level = 1
        while self.calc_xp(level) <= xp:
            level += 1
        return level - 1
    
    def calc_xp(self, level: int) -> int:
        total = 0
        for i in range(level - 1):
            total += self.game.level_one * (int(self.game.level_mult) ** i)
        return int(total)
