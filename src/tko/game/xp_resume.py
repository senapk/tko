from tko.game.quest import Quest

class SkillResume:
    def __init__(self):
        self.obtained: dict[str, float] = {}
        self.target100: dict[str, float] = {}
        self.all_items: dict[str, float] = {}

class XPResume:
    def __init__(self, quests: dict[str, Quest], remote: str | None = None):
        self.remote = remote
        if remote is not None:
            self.quests: dict[str, Quest] = {}
            for k, q in quests.items():
                if q.basic.remote_name == remote:
                    self.quests[k] =  q
        else:
            self.quests = quests

    def get_xp_resume(self):
        total = 0
        obtained = 0
        for q in self.quests.values():
            o, _, t = q.progress.get_obtained_goal_available()
            total += t
            obtained += o
        return obtained, total

    def get_skills_resume(self) -> SkillResume:
        all_available: dict[str, float] = {}
        obtained: dict[str, float] = {}
        target: dict[str, float] = {}

        for q in self.quests.values():
            for skill in q.config.skills:
                target[skill] = target.get(skill, 0) + q.config.goal_xp * q.config.factor
            for t in q.get_tasks():
                for skill in t.game.skills:
                    if skill == "":
                        continue
                    gvalue = (q.config.factor * t.game.xp * t.grader.ratio)
                    if gvalue < 0.1:
                        gvalue = 0
                    obtained[skill] = obtained.get(skill, 0) + gvalue
                    all_available[skill] = all_available.get(skill, 0) + q.config.factor * t.game.xp

        resume = SkillResume()
        resume.obtained = obtained
        resume.target100 = target
        resume.all_items = all_available
        return resume

    def sum_xp(self, resume: SkillResume) -> tuple[float, float, float]:
        total_obtained = 0
        total_target100 = 0
        total_complete = 0
        for key, value in resume.all_items.items():
            total_obtained += resume.obtained.get(key, 0)
            total_target100 += resume.target100.get(key, 0)
            total_complete += value
        return total_obtained, total_target100, total_complete