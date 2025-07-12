class QuestGrader:
    class Elem:
        def __init__(self, opt: bool, value: int, percent: float):
            self.opt = opt
            self.value = value
            self.percent = percent

    @staticmethod
    def calc_xp_earned_total(tasks: list[Elem]) -> tuple[float, float]:
        """
        tasks: list of tuples (opt, xp, percent)
        """
        total_xp = 0.0
        earned_xp = 0.0
        for elem in tasks:
            if not elem.opt:
                total_xp += elem.value
            if elem.percent > 0:
                earned_xp += elem.value * (elem.percent / 100.0)
        return earned_xp, total_xp
    
    @staticmethod
    def get_percent(earned_xp: float, total_xp: float) -> float:
        if total_xp == 0:
            return 0.0
        return (earned_xp * 100.0) / total_xp