from tko.game.game import Game
from tko.widget.bar_builder import BarBuilder
from tko.widget.colors import Colors
from tko.widget.frame import Frame
from tko.config.flags import Flags
from tko.util.rt import RT
from tko.game.xp_resume import XPResume


class GuiSkillsBar:

    def __init__(self, game: Game, colors: Colors, flags: Flags):
        self.game = game
        self.style = BarBuilder()
        self.colors = colors
        self.flags = flags

    def build_list_sentence(self, items: list[RT]) -> list[RT]:
        out: list[RT] = []
        for x in items:
            color_ini = x[0].runs[0][0] if x[0].runs else ""
            color_end = x[-1].runs[0][0] if x[-1].runs else ""
            left = RT(" ", color_ini)
            right = RT(" ", color_end)
            middle = x
            if x.plain().startswith("!"):
                middle = x.slice(1)
            out.append(left + middle + right)
        return out

    def make_xp_button(self, size: int) -> RT:
        xp_resume = XPResume(self.game.quests)
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

    def show(self, frame_xp: Frame) -> None:
        dy, dx = frame_xp.get_inner()
        xp_resume = XPResume(self.game.quests)
        resume = xp_resume.get_skills_resume()
        frame_xp.draw()

        elements: list[RT] = []
        for skill, value in resume.all_items.items():
            if self.flags.show_panel.is_true():
                obtained_value = round(100 * resume.obtained.get(skill, 0) / resume.target100.get(skill, 1))
                possible_value = round(100 * value / resume.target100.get(skill, 1))
                text = f"{skill}: {obtained_value:03d}%  {possible_value:03d}%"
            else:
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
            elements.append(skill_bar)

        # Total bar
        total_obtained, total_target100, total_complete = xp_resume.sum_xp(resume)
        if total_target100 == 0:
            grade = 0
        else:
            grade = total_obtained / total_target100 * 10.0

        if self.flags.show_panel.is_true():
            text = f" Nota: {grade:.1f}       "
        else:
            text = f"Nota: {grade:.1f} :{round(total_obtained):03d}/{round(total_target100):03d}/{round(total_complete):03d}"
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
