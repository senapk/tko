import pytest
from tko.game.xp_resume import XPResume, SkillResume
from unittest.mock import MagicMock

class DummyProgress:
    def __init__(self, o: float, t: float) -> None:
        self.o: float = o
        self.t: float = t
    def get_xp(self) -> tuple[float, float]:
        return self.o, self.t
    def get_obtained_goal_available(self) -> tuple[float, float, float]:
        return self.o, self.t, self.t

class DummyTask:
    def __init__(self, skill: str | None, xp: float, ratio: float) -> None:
        self.game = MagicMock()
        self.game.skill = skill
        self.game.xp = xp
        self.grader = MagicMock()
        self.grader.ratio = ratio

class DummyQuest:
    def __init__(
        self,
        name: str,
        progress: DummyProgress,
        skill: str | None,
        goal_xp: float,
        tasks: list[DummyTask],
    ) -> None:
        self.name: str = name
        self.progress: DummyProgress = progress
        self.game = MagicMock()
        self.game.skill = skill
        self.game.goal_xp = goal_xp
        self._tasks: list[DummyTask] = tasks
    def get_tasks(self) -> list[DummyTask]:
        return self._tasks

@pytest.fixture
def sample_quests() -> dict[str, DummyQuest]:
    q1 = DummyQuest(
        "q1",
        DummyProgress(10, 20),
        "python",
        100.0,
        [DummyTask("python", 50.0, 1.0), DummyTask("oop", 50.0, 0.5)]
    )
    q2 = DummyQuest(
        "q2",
        DummyProgress(5, 10),
        "algorithms",
        200.0,
        [DummyTask("algorithms", 100.0, 1.0), DummyTask(None, 30.0, 1.0)]
    )
    q3 = DummyQuest(
        "q3",
        DummyProgress(0, 0),
        "oop",
        50.0,
        [],
    )
    return {"q1": q1, "q2": q2, "q3": q3}

def test_get_xp_resume(sample_quests: dict[str, DummyQuest]) -> None:
    xp = XPResume(sample_quests) # type: ignore
    obtained, total = xp.get_xp_resume()
    assert obtained == 15
    assert total == 30

def test_get_skills_resume(sample_quests: dict[str, DummyQuest]) -> None:
    xp = XPResume(sample_quests) # type: ignore
    resume: dict[str, SkillResume] = xp.get_skills_resume()

    assert set(resume.keys()) == {"python", "oop", "algorithms"}
    assert resume["python"] == SkillResume(obtained=50.0, target100=100.0, available=50.0)
    assert resume["oop"] == SkillResume(obtained=25.0, target100=50.0, available=50.0)
    assert resume["algorithms"] == SkillResume(obtained=100.0, target100=200.0, available=100.0)

def test_sum_xp(sample_quests: dict[str, DummyQuest]) -> None:
    xp = XPResume(sample_quests) # type: ignore
    resume: dict[str, SkillResume] = xp.get_skills_resume()
    sk_resume = xp.sum_xp(resume, overload=1.1)
    assert isinstance(sk_resume.obtained, float)
    assert isinstance(sk_resume.target100, float)
    assert isinstance(sk_resume.available, float)
    assert sk_resume.obtained == 175.0
    assert sk_resume.target100 == 350.0
    assert sk_resume.available == 200.0
