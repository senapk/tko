from tko.game.quest import Quest


class XPResume:
    def __init__(self, quests: dict[str, Quest]):
        self.quests = quests

    def get_xp_resume(self):
        total = 0
        obtained = 0
        for q in self.quests.values():
            o, t = q.progress.get_xp()
            total += t
            obtained += o
        return obtained, total

    def get_skills_resume(self) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
        all_available: dict[str, float] = {}
        obtained: dict[str, float] = {}
        target: dict[str, float] = {}

        for q in self.quests.values():
            for skill, factor in q.config.skills.items():
                target[skill] = target.get(skill, 0) + q.config.total_xp * factor
            for t in q.get_tasks():
                for skill, factor in t.game.skills.items():
                    if skill == "":
                        continue
                    gvalue = (factor * t.game.xp * t.grader.ratio)
                    if gvalue < 0.1:
                        gvalue = 0
                    obtained[skill] = obtained.get(skill, 0) + gvalue
                    all_available[skill] = all_available.get(skill, 0) + factor * t.game.xp

        return obtained, target, all_available

    def sum_xp(self, obtained: dict[str, float], target: dict[str, float], complete: dict[str, float]) -> tuple[float, float, float]:
        total_obtained = 0
        total_priority = 0
        total_complete = 0
        for key, value in complete.items():
            total_obtained += obtained.get(key, 0)
            total_complete += value
        return total_obtained, total_priority, total_complete