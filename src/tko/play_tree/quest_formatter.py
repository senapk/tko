from tko.game.quest import Quest
from tko.config.settings import Settings
from tko.play.quest_visibility_service import QuestVisibilityService
from tko.util.rt import RT
from tko.play_tree.time_formatter import TimeFormatter


class QuestFormatter:
    def __init__(self, settings: Settings, time_formatter: TimeFormatter):
        self.settings = settings
        self.time_formatter = time_formatter

    def count_visible_hidden_tasks(self, quest: Quest) -> tuple[int, int]:
        visible = 0
        hidden = 0
        for task in quest.get_tasks():
            if task.ui.visible:
                visible += 1
            else:
                hidden += 1
        return visible, hidden

    def get_percent_text(self, quest: Quest) -> RT:
        pall = quest.progress.get_percent()
        percent_text = self.time_formatter.format_percent_3s(pall).set_style("g")
        return percent_text

    def get_quest_full_title(self, quest: Quest, show_skills: bool) -> RT:
        output = RT(quest.basic.remote_name, "c") + RT(":") + RT(quest.basic.title)
        if show_skills:
            for skill, value in quest.config.skills.items():
                if value > 1:
                    output += RT.run("b", f" +{skill}*{value}")
                else:
                    output += RT.run("b", f" +{skill}")
        return output

    def get_focus_color_quest(self, quest: Quest) -> str:
        if not QuestVisibilityService.is_reachable(quest):
            return "R"
        return self.settings.colors.focused_item