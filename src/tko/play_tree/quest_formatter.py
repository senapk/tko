from tko.game.quest import Quest
from tko.util.rt import RT


class QuestFormatter:
    def get_quest_full_title(self, quest: Quest, show_skills: bool, sep: str = " ") -> RT:
        output = RT(quest.basic.source_name, "c") + RT(":") + RT(quest.basic.title)
        if show_skills:
            if quest.game.skill is not None:
                output += RT.run("g", f"{sep}+{quest.game.skill}")
        return output
