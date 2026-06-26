from tko.game.game import Game
from tko.widget.bar_builder import BarBuilder
from tko.widget.colors import Colors
from tko.widget.frame import Frame
from tko.config.flags import Flags
from tko.util.rt import RT
from tko.game.xp_resume import SkillResume, XPResume
from typing import Callable
from tko.game.quest import Quest


class GuiSkillsBar:

    def __init__(self, game: Game, colors: Colors, flags: Flags, remote: Callable[[], str]):
        self.game = game
        self.style = BarBuilder()
        self.colors = colors
        self.flags = flags
        self.remote = remote
        self.target_cut_factor = 1.2 # use 0 to show all

        self.name_size = 8
        self.obtained_cut = 3
        self.target_cut = 3
        self.available_cut = 3
        self.overload = 1.1

    def get_remote(self):
        try:
            return self.remote()
        except IndexError as _:
            return ""

    def get_entry_xp(self, resume_dict: dict[str, SkillResume], skill: str, target_value: float, dx: int) -> RT:
        obtained_value = resume_dict[skill].obtained
        target100_value = resume_dict[skill].target100
        available_value = resume_dict[skill].available
        title = f"{skill[:self.name_size]:<{self.name_size}}"
        obtained = f"{round(obtained_value):>{self.obtained_cut}}"
        target = f"{round(target100_value):>{self.target_cut}}"
        available = f"{round(available_value):>{self.available_cut}}"
        text = RT(f"{title}:{obtained}/{target}/{available}", "X")
        
        skill_bar = self.style.build_progress_xp(
            obtained=obtained_value,
            target100=target100_value,
            available=min(available_value, target_value),
            reference=target_value,
            length=dx - (self.target_cut + self.available_cut + self.obtained_cut + 3 + self.name_size + 3)
        )
        return text + " " + skill_bar

    def get_entry_perc(self, resume_dict: dict[str, SkillResume], skill: str, value: float, dx: int) -> RT:
        obtained_value = round(resume_dict[skill].obtained)
        target100_value = round(resume_dict[skill].target100)
        complete_value = round(value)
        text = f"{skill}:{obtained_value:03d}/{target100_value:03d}/{complete_value:03d}"
        perc = resume_dict[skill].obtained / resume_dict[skill].target100 if resume_dict[skill].target100 != 0 else 0
        done_color = self.colors.progress_skill_done
        todo_color = self.colors.progress_skill_todo
        skill_bar = self.style.build_bar(
            text=text,
            percent=perc,
            length=dx - 2,
            fmt_true=done_color,
            fmt_false=todo_color,
        )
        return skill_bar

    def show(self, frame_xp: Frame) -> None:
        dy, dx = frame_xp.get_inner()
        quests: dict[str, Quest] = {k: q for k, q in self.game.quests.items() if q.basic.remote_name == self.get_remote()}
        xp_resume: XPResume = XPResume(quests)
        skills_resume: dict[str, SkillResume] = xp_resume.get_skills_resume()
        frame_xp.draw()

        elements: list[RT] = []

        available_list = [x.available for x in skills_resume.values()]
        obtained_list = [x.obtained for x in skills_resume.values()]
        target_list = [x.target100 for x in skills_resume.values()]

        max_obtained = max(obtained_list) if len(obtained_list) > 0 else 0
        max_target = max(target_list) if len(target_list) > 0 else 0
        max_available = max(available_list) if len(available_list) > 0 else 0

        self.obtained_cut = 3 if max_obtained > 99 else (2 if max_obtained > 9 else 1)
        self.target_cut = 3 if max_target > 99 else 2
        self.available_cut = 3 if max_available > 99 else 2
        
        if self.target_cut_factor == 0:
            reference_value = max_available
        else:
            reference_value = max_target * self.target_cut_factor


        for skill in skills_resume.keys():
            elements.append(self.get_entry_xp(skills_resume, skill, reference_value, dx))

        # Total bar
        resume = xp_resume.sum_xp(skills_resume, self.overload)
        if resume.target100 == 0:
            grade = 0
        else:
            grade = resume.obtained / resume.target100 * 10.0

        # if self.flags.show_panel.is_true():
        text = f" Nota: {grade:.1f}       "
        # else:
        #     text = f"Nota: {grade:.1f} :{round(total_obtained):03d}/{round(total_target100):03d}/{round(total_complete):03d}"
        done_color = self.colors.main_bar_done
        todo_color = self.colors.main_bar_todo
        percent = resume.obtained / resume.target100 if resume.target100 > 0 else 0.0
        total_bar = self.style.build_bar(text, percent, dx - 2, done_color, todo_color)
        elements.append(total_bar)

        # printing — calculating line breaks
        line_breaks = dy - len(elements)
        for skill_bar in elements:
            frame_xp.print(1, skill_bar)
            if line_breaks > 0:
                line_breaks -= 1
                frame_xp.print(1, RT())
