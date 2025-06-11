from tko.game.task import Task
from tko.play.floating import Floating
from tko.play.fmt import Fmt
from tko.play.input_manager import InputManager
from tko.util.symbols import symbols
from tko.util.text import Text
from tko.play.keys import GuiKeys
from tko.settings.settings import Settings
# from typing import override

import curses


class FloatingGrade(Floating):
    def __init__(self, task: Task, settings: Settings, _align: str =""):
        super().__init__(settings, _align)
        self.settings = settings
        self._task = task
        self._line = 0 if not task.is_leet_code() else 1
        self.set_text_ljust()
        self._frame.set_border_color("g")
        self.set_header_text(Text.format("{y/}", " Utilize os direcionais e teclas - e + para  marcar "))
        self.set_footer_text(Text.format("{y/}", " Pressione Enter para confirmar "))

        self.grades_index = [task.coverage // 10, task.approach, task.autonomy, task.how_neat, task.how_cool, task.how_easy]
        self.coverage = ["x", "1", "2", "3", "4", "5", "6", "7", "8", "9", "✓"]
        self.coverage_msg = [
            Text().addf("m", "Não ").addf("y", "fiz"),
            Text().addf("m", "Fiz ").addf("y", "10%"),
            Text().addf("m", "Fiz ").addf("y", "20%"),
            Text().addf("m", "Fiz ").addf("y", "30%"),
            Text().addf("m", "Fiz ").addf("y", "40%"),
            Text().addf("m", "Fiz ").addf("y", "50%"),
            Text().addf("m", "Fiz ").addf("y", "60%"),
            Text().addf("m", "Fiz ").addf("y", "70%"),
            Text().addf("m", "Fiz ").addf("y", "80%"),
            Text().addf("m", "Fiz ").addf("y", "90%"),
            Text().addf("m", "Fiz ").addf("y", "100%")]
        self.approach = [x.text for x in [symbols.approach_x, symbols.approach_e, symbols.approach_d, symbols.approach_c, symbols.approach_b, symbols.approach_a, symbols.approach_s]]
        self.approach_msg = [
            Text().addf("m", "Não fiz"),
            Text().addf("m", "Peguei o código ").addf("y", "pronto").addf("m", " e estudei ele"),
            Text().addf("m", "Fiz com ajuda de ").addf("y", "IA").addf("m", "(copilot|gpt|outros)"),
            Text().addf("m", "Fiz").addf("y"," guiado ").addf("m", "por aula|vídeo|colega|monitor"),
            Text().addf("y", "(Re)Fiz").addf("m", " os códigos").addf("m", " pesquisando"),
            Text().addf("y", "Refiz sozinho").addf("m", " sem consultar algoritmos"),
            Text().addf("y", "Fiz sozinho").addf("m", " sem consultar algoritmos")
            ]
        self.autonomy = [x.text for x in [symbols.autonomy_x, symbols.autonomy_e, symbols.autonomy_d, symbols.autonomy_c, symbols.autonomy_b, symbols.autonomy_a]]
        self.autonomy_msg = [
            Text().addf("m", "Não fiz        ").addf("y", "                         "),
            Text().addf("m", "Consigo refazer ").addf("y", ">= 30% sem consulta     "),
            Text().addf("m", "Consigo refazer ").addf("y", ">= 50% sem consulta     "),
            Text().addf("m", "Consigo refazer ").addf("y", ">= 70% sem consulta     "),
            Text().addf("m", "Consigo refazer ").addf("y", ">= 90% sem consulta     "),
            Text().addf("m", "Consigo refazer ").addf("y", "  100% sem consulta     ")
            ]

        self.neat = [x.text for x in [symbols.cool_x, 
                                             symbols.cool_e, 
                                             symbols.cool_d, 
                                             symbols.cool_c, 
                                             symbols.cool_b, 
                                             symbols.cool_a]]
 
        self.neat_msg = [
            Text().addf("m", "Sem opinião               "),
            Text().addf("m", "A descrição da atividades ").addf("y", "é confusa     "),
            Text().addf("m", "A descrição da atividades ").addf("y", "é insuficiente"),
            Text().addf("m", "A descrição da atividades ").addf("y", "é razoável    "),
            Text().addf("m", "A descrição da atividades ").addf("y", "é adequada    "),
            Text().addf("m", "A descrição da atividades ").addf("y", "é excelente   ")
            ]
        
       
        self.cool = [x for x in self.neat]
        self.cool_msg = [
            Text().addf("m", "Sem opinião        ").addf("y", "                     "),
            Text().addf("m", "A atividade parece ").addf("y", "muito desinteressante"),
            Text().addf("m", "A atividade parece ").addf("y", "desinteressante      "),
            Text().addf("m", "A atividade parece ").addf("y", "indiferente          "),
            Text().addf("m", "A atividade parece ").addf("y", "interessante         "),
            Text().addf("m", "A atividade parece ").addf("y", "muito interessante   "),
            ]

        self.easy = [x for x in self.neat]
        self.easy_msg = [
            Text().addf("m", "Sem opinião          ").addf("y", "                   "),
            Text().addf("m", "Resolver a atividade ").addf("y", "foi muito difícil  "),
            Text().addf("m", "Resolver a atividade ").addf("y", "foi difícil        "),
            Text().addf("m", "Resolver a atividade ").addf("y", "foi razoável       "),
            Text().addf("m", "Resolver a atividade ").addf("y", "foi fácil          "),
            Text().addf("m", "Resolver a atividade ").addf("y", "foi muito fácil    "),
            ]

        self.grades_value = [self.coverage, self.approach, self.autonomy, self.neat, self.cool, self.easy]
        self.grades_msg = [self.coverage_msg, self.approach_msg, self.autonomy_msg, self.neat_msg, self.cool_msg, self.easy_msg]


    def update_content(self):
        self._content = []
        self._content.append(Text().add("         Pontue de acordo com a última fez que você (re)fez a tarefa do zero         "))
        self._content.append(Text().add("╔══════════════════════════════════ Obrigatório ═════════════════════════════════════"))
        coverage_question = "Cobertura: Quanto entregou?"
        approach_question = "Abordagem: Como foi feito ?"
        autonomy_question = "Autonomia: Quanto domina  ?"
        neat_question = "Descrição: É bem escrita  ?"
        cool_question = "Interesse: É interessante ?"
        easy_question = "Dedicação: É fácil        ?"

        opening = "╠═ "
        op_prefix = opening if not self._task.is_leet_code() else "║  "
        coverage_text = Text().add(op_prefix).addf("Y" if self._line == 0 else "", coverage_question).add("  ")
        for i, c in enumerate(self.coverage):
            coverage_text.addf("C" if i == self.grades_index[0] else "", c)
        coverage_text.add("  ").add(self.coverage_msg[self.grades_index[0]])
        self._content.append(coverage_text)
        # self._content.append(Text())
        approach_text = Text().add(opening).addf("Y" if self._line == 1 else "", approach_question).add("  ")
        for i, c in enumerate(self.approach):
            approach_text.addf("G" if i == self.grades_index[1] else "", c).add("")
            if c == "x":
                approach_text.add("  ")
            if c == "A":
                approach_text.add("  ")
            if c == "S":
                approach_text.add(" ")
        
        approach_text.add(" ").add(self.approach_msg[self.grades_index[1]])
        self._content.append(approach_text)
        # self._content.append(Text())

        prefix = opening
        if self.done_alone():
            prefix = "║  "
        autonomy_text = Text().add(prefix).addf("Y" if self._line == 2 else "", autonomy_question).add("  ")
        for i, c in enumerate(self.autonomy):
            autonomy_text.addf("yW" if i == self.grades_index[2] else "", c).add(" ")
        autonomy_text.add(" ").add(self.autonomy_msg[self.grades_index[2]])
        self._content.append(autonomy_text)

        self._content.append(Text().add("╟─────────────────────────────────── Opcional ───────────────────────────────────────"))

        description_text = Text().add(opening).addf("Y" if self._line == 3 else "", neat_question).add("  ")
        for i, c in enumerate(self.neat):
            description_text.addf("yW" if i == self.grades_index[3] else "", c).add(" ")
        description_text.add(" ").add(self.neat_msg[self.grades_index[3]])
        self._content.append(description_text)

        desire_text = Text().add(opening).addf("Y" if self._line == 4 else "", cool_question).add("  ")
        for i, c in enumerate(self.cool):
            desire_text.addf("yW" if i == self.grades_index[4] else "", c).add(" ")
        desire_text.add(" ").add(self.cool_msg[self.grades_index[4]])
        self._content.append(desire_text)

        effort_text = Text().add(opening).addf("Y" if self._line == 5 else "", easy_question).add("  ")
        for i, c in enumerate(self.easy):
            effort_text.addf("yW" if i == self.grades_index[5] else "", c).add(" ")
        effort_text.add(" ").add(self.easy_msg[self.grades_index[5]])
        self._content.append(effort_text)

        self._content.append(Text().add("╚════════════════════════════════════════════════════════════════════════════════════"))

    # @override
    def draw(self):
        self._set_default_header()
        self._set_default_footer()
        self.setup_frame()
        self._frame.draw()
        self.update_content()
        self.write_content()

    def change_task(self):
        if not self._task.is_leet_code():
            self._task.set_coverage(self.grades_index[0] * 10)
        self._task.set_approach(self.grades_index[1])
        self._task.set_autonomy(self.grades_index[2])
        self._task.set_description(self.grades_index[3])
        self._task.set_desire(self.grades_index[4])
        self._task.set_effort(self.grades_index[5])

    def done_alone(self) -> bool:
        return self.grades_index[1] > 4
    
    def set_autonomy_max(self):
        self.grades_index[2] = 5

    def send_key_up(self):
        if not(self._task.is_leet_code() and self._line == 1):
            self._line = max(self._line - 1, 0)
        if (self.done_alone() and self._line == 2):
            self._line = max(self._line - 1, 0)

    def send_key_down(self):
        self._line = min(self._line + 1, len(self.grades_index) - 1)
        if self.done_alone() and self._line == 2:
            self._line = min(self._line + 1, len(self.grades_index) - 1)

    def send_key_left(self):
        self.grades_index[self._line] = max(self.grades_index[self._line] - 1, 0)
        if self._line == 1 and self.grades_index[1] < 4:
            self.grades_index[2] = 0
        self.change_task()

    def send_key_right(self):
        self.grades_index[self._line] = min(self.grades_index[self._line] + 1, len(self.grades_value[self._line]) - 1)
        if self._line == 1 and self.done_alone() and self.grades_index[self._line] > 4:
            self.set_autonomy_max()
        self.change_task()

    # @override
    def get_input(self) -> int:
        self.draw()
        key: int = Fmt.getch()
        key = InputManager.fix_cedilha(Fmt.get_screen(), key)
        if key == self.settings.app.get_key_up() or key == ord(GuiKeys.up) or key == ord(GuiKeys.up2):
            self.send_key_up()
        elif key == self.settings.app.get_key_down() or key == ord(GuiKeys.down) or key == ord(GuiKeys.down2):
            self.send_key_down()
        elif key == self.settings.app.get_key_left() or key == ord(GuiKeys.left) or key == ord(GuiKeys.left2):
            self.send_key_left()
        elif key == self.settings.app.get_key_right() or key == ord(GuiKeys.right) or key == ord(GuiKeys.right2):
            self.send_key_right()
        elif key == ord("+") or key == ord("="):
            for _ in range(10):
                self.send_key_right()
            self.send_key_down()
        elif key == ord("-"):
            for _ in range(10):
                self.send_key_left()
            self.send_key_up()

        elif key == ord('\n') or key == curses.KEY_BACKSPACE or key == InputManager.esc:
            self._enable = False
            if self._exit_fn is not None:
                self._exit_fn()
        return -1