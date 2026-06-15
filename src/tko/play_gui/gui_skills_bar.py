from tko.game.game import Game
from tko.widget.bar_builder import BarBuilder
from tko.widget.colors import Colors
from tko.widget.frame import Frame
from tko.config.flags import Flags
from tko.util.rt import RT
from tko.game.xp_resume import SkillResume, XPResume
from typing import Callable


class GuiSkillsBar:

    def __init__(self, game: Game, colors: Colors, flags: Flags, remote: Callable[[], str]):
        self.game = game
        self.style = BarBuilder()
        self.colors = colors
        self.flags = flags
        self.remote = remote
        self.target_cut_factor = 1.2

        self.name_size = 8
        self.obtained_cut = 3
        self.target_cut = 3
        self.available_cut = 3

    def get_remote(self):
        try:
            return self.remote()
        except IndexError as _:
            return ""

    def make_xp_button(self, size: int) -> RT:

        xp_resume = XPResume(self.game.quests, self.get_remote())
        resume = xp_resume.get_skills_resume()

        keys_to_remove: list[str] = []
        for skill, value in resume.obtained.items():
            if value < 1:
                keys_to_remove.append(skill)

        for key in keys_to_remove:
            if key in resume.obtained:
                del resume.obtained[key]
            if key in resume.target100:
                del resume.target100[key]
            if key in resume.all_items:
                del resume.all_items[key]

        qtd = len(resume.obtained)
        if qtd == 0:
            text = " Nenhuma habilidade disponível "
            percent = 0.0
            return self.style.build_bar(text, percent, size, "W", "W")

        skill_size = int(size / qtd)

        elements: list[RT] = []
        for skill, _ in resume.all_items.items():
            text = f"{skill}"
            perc = resume.obtained.get(skill, 0) / resume.target100.get(skill, 1)
            done_color = self.colors.main_bar_done
            todo_color = self.colors.main_bar_todo
            skill_bar = self.style.build_bar(
                text=text,
                percent=perc,
                length=skill_size - 2,
                fmt_true=done_color,
                fmt_false=todo_color,
            )
            elements.append(skill_bar)
        cover_color = "K"
        xpbar =  RT(" █", cover_color.lower())
        for skill_bar in elements:
            xpbar += skill_bar + RT("█", cover_color.lower())
        xpbar += RT("█", cover_color.lower())
        return xpbar

    def get_entry_xp(self, resume: SkillResume, skill: str, target_value: float, dx: int) -> RT:
        obtained_value = resume.obtained.get(skill, 0)
        target100_value = resume.target100.get(skill, 0)
        available_value = resume.all_items.get(skill, 0)
        reference_value = target_value
        skill_bar = self.style.build_progress_xp(
            obtained=obtained_value,
            target100=target100_value,
            available=min(available_value, target_value),
            reference=reference_value,
            length=dx - (self.target_cut + self.available_cut + self.obtained_cut + 3 + self.name_size + 3),
            styles=("Y", "G", "")
        )
        text = RT(f"{skill[:self.name_size]:<{self.name_size}}:{round(obtained_value):>{self.obtained_cut}}/{round(target100_value):>{self.target_cut}}/{round(available_value):>{self.available_cut}}", "X")
        return text + " " + skill_bar

    def get_entry_perc(self, resume: SkillResume, skill: str, value: float, dx: int, cut: int, name_size: int) -> RT:
        obtained_value = round(resume.obtained.get(skill, 0))
        target100_value = round(resume.target100.get(skill, 0))
        complete_value = round(value)
        text = f"{skill}:{obtained_value:03d}/{target100_value:03d}/{complete_value:03d}"
        perc = resume.obtained.get(skill, 0) / resume.target100.get(skill, 1)
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
        xp_resume = XPResume(self.game.quests, self.get_remote())
        skills_resume = xp_resume.get_skills_resume()
        frame_xp.draw()

        elements: list[RT] = []

        max_obtained = max([x for x in skills_resume.obtained.values()])
        max_target = max([x for x in skills_resume.target100.values()])
        max_available = max([x for x in skills_resume.all_items.values()])
        self.obtained_cut = 3 if max_obtained > 99 else (2 if max_obtained > 9 else 1)
        self.target_cut = 3 if max_target > 99 else 2
        self.available_cut = 3 if max_available > 99 else 2
        
        for skill in skills_resume.all_items.keys():
            elements.append(self.get_entry_xp(skills_resume, skill, max_target * self.target_cut_factor, dx))

        # Total bar
        total_obtained, total_target100, _ = xp_resume.sum_xp(skills_resume)
        if total_target100 == 0:
            grade = 0
        else:
            grade = total_obtained / total_target100 * 10.0

        # if self.flags.show_panel.is_true():
        text = f" Nota: {grade:.1f}       "
        # else:
        #     text = f"Nota: {grade:.1f} :{round(total_obtained):03d}/{round(total_target100):03d}/{round(total_complete):03d}"
        done_color = self.colors.main_bar_done
        todo_color = self.colors.main_bar_todo
        percent = total_obtained / total_target100 if total_target100 > 0 else 0.0
        total_bar = self.style.build_bar(text, percent, dx - 2, done_color, todo_color)
        elements.append(total_bar)

        # printing — calculating line breaks
        line_breaks = dy - len(elements)
        for skill_bar in elements:
            frame_xp.print(1, skill_bar)
            if line_breaks > 0:
                line_breaks -= 1
                frame_xp.print(1, RT())
