from tko.game.quest import Quest


class XPResume:
    def __init__(self, quests: dict[str, Quest]):
        self.quests = quests

    def get_xp_resume(self, include_main: bool, include_side: bool):
        total = 0
        obtained = 0
        for q in self.quests.values():
            o, t = q.get_xp(include_main_perk=include_main, include_side=include_side)
            total += t
            obtained += o
        return obtained, total

    def get_skills_resume(self) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
        # obtained, priority, complete
        priority: dict[str, float] = {}
        complete: dict[str, float] = {}
        obtained: dict[str, float] = {}

        for q in self.quests.values():
            for t in q.get_tasks():
                for skill, value in t.game.skills.items():
                    if skill == "":
                        continue
                    gvalue = (value * t.game.xp * t.grader.ratio)
                    if gvalue < 0.1:
                        gvalue = 0
                    obtained[skill] = obtained.get(skill, 0) + gvalue
                    if not t.config.is_optional:
                        priority[skill] = priority.get(skill, 0) + value * t.game.xp
                    complete[skill] = complete.get(skill, 0) + value * t.game.xp

        return obtained, priority, complete

    def sum_xp(self, obtained: dict[str, float], priority: dict[str, float], complete: dict[str, float]) -> tuple[float, float, float]:
        total_obtained = 0
        total_priority = 0
        total_complete = 0
        for key, value in complete.items():
            total_obtained += obtained.get(key, 0)
            total_priority += priority.get(key, 0)
            total_complete += value
        return total_obtained, total_priority, total_complete