import pytest
from tko.game.xp_resume import XPResume, SkillResume
from unittest.mock import MagicMock

class DummyProgress:
    def __init__(self, o: float, t: float) -> None:
        self.o: float = o
        self.t: float = t
    def get_xp(self) -> tuple[float, float]:
        return self.o, self.t

class DummyTask:
    def __init__(self, skills: list[str], xp: float, ratio: float) -> None:
        self.game = MagicMock()
        self.game.skills = skills
        self.game.xp = xp
        self.grader = MagicMock()
        self.grader.ratio = ratio

class DummyQuestConfig:
    def __init__(self, skills: list[str], goal_xp: float, factor: float) -> None:
        self.skills: list[str] = skills
        self.goal_xp: float = goal_xp
        self.factor: float = factor

class DummyQuest:
    def __init__(self, name: str, progress: DummyProgress, config: DummyQuestConfig, tasks: list[DummyTask]) -> None:
        self.name: str = name
        self.progress: DummyProgress = progress
        self.config: DummyQuestConfig = config
        self._tasks: list[DummyTask] = tasks
    def get_tasks(self) -> list[DummyTask]:
        return self._tasks

@pytest.fixture
def sample_quests() -> dict[str, DummyQuest]:
    q1 = DummyQuest(
        "q1",
        DummyProgress(10, 20),
        DummyQuestConfig(["python", "oop"], 100, 1.0),
        [DummyTask(["python"], 50, 1.0), DummyTask(["oop"], 50, 0.5)]
    )
    q2 = DummyQuest(
        "q2",
        DummyProgress(5, 10),
        DummyQuestConfig(["algorithms"], 200, 0.5),
        [DummyTask(["algorithms"], 100, 1.0)]
    )
    return {"q1": q1, "q2": q2}

def test_get_xp_resume(sample_quests: dict[str, DummyQuest]) -> None:
    xp = XPResume(sample_quests) # type: ignore
    obtained, total = xp.get_xp_resume()
    assert obtained == 15
    assert total == 30

def test_get_skills_resume(sample_quests: dict[str, DummyQuest]) -> None:
    xp = XPResume(sample_quests) # type: ignore
    resume: SkillResume = xp.get_skills_resume()
    assert isinstance(resume, SkillResume)
    # Check keys
    assert set(resume.obtained.keys()) == {"python", "oop", "algorithms"}
    assert set(resume.target100.keys()) == {"python", "oop", "algorithms"}
    assert set(resume.all_items.keys()) == {"python", "oop", "algorithms"}
    # Check values are floats
    for v in resume.obtained.values():
        assert isinstance(v, float)
    for v in resume.target100.values():
        assert isinstance(v, float)
    for v in resume.all_items.values():
        assert isinstance(v, float)

def test_sum_xp(sample_quests: dict[str, DummyQuest]) -> None:
    xp = XPResume(sample_quests) # type: ignore
    resume: SkillResume = xp.get_skills_resume()
    total_obtained: float
    total_target100: float
    total_complete: float
    total_obtained, total_target100, total_complete = xp.sum_xp(resume)
    assert isinstance(total_obtained, float)
    assert isinstance(total_target100, float)
    assert isinstance(total_complete, float)
    # Should be consistent with resume values
    assert abs(total_obtained - sum(resume.obtained.values())) < 1e-6
    assert abs(total_target100 - sum(resume.target100.values())) < 1e-6
    assert abs(total_complete - sum(resume.all_items.values())) < 1e-6
