from dataclasses import dataclass

from tko.game.quest import Quest

@dataclass(frozen=True)
class SkillResume:
    obtained: float
    target100: float
    available: float

class XPResume:
    def __init__(self, quests: dict[str, Quest]):
        self.quests = quests

    def get_xp_resume(self):
        total = 0
        obtained = 0
        for q in self.quests.values():
            o, _, t = q.progress.get_obtained_goal_available()
            total += t
            obtained += o
        return obtained, total

    def get_skills_resume(self) -> dict[str, SkillResume]:
        available: dict[str, float] = {}
        obtained: dict[str, float] = {}
        target100: dict[str, float] = {}

        for q in self.quests.values():
            if q.game.skill is not None:
                skill = q.game.skill
                target100[skill] = target100.get(skill, 0) + q.game.goal_xp
            for t in q.get_tasks():
                skill = t.game.skill
                if skill is None:
                    continue
                gvalue = t.game.xp * t.grader.ratio
                if gvalue < 0.1:
                    gvalue = 0
                obtained[skill] = obtained.get(skill, 0) + gvalue
                available[skill] = available.get(skill, 0) + t.game.xp
        output: dict[str, SkillResume] = {}
        for skill, value in available.items():
            resume = SkillResume(
                obtained=obtained.get(skill, 0),
                target100=target100.get(skill, 0),
                available=value
            )
            output[skill] = resume

        return output

    def sum_xp(self, resume_dict: dict[str, SkillResume], overload: float) -> SkillResume:
        total_obtained = 0
        total_target100 = 0
        total_available = 0
        for resume in resume_dict.values():
            target = resume.target100
            total_target100 += target
            obtained = resume.obtained
            total_obtained += min(obtained, target * overload)
            total_available += resume.available
        return SkillResume(
            obtained=total_obtained,
            target100=total_target100,
            available=total_available
        )