from tko.game.task import Task
from tko.play.floating import Floating
from tko.play.fmt import Fmt
from tko.play.input_manager import InputManager
from tko.util.symbols import symbols
from tko.util.text import Text
from tko.play.keys import GuiKeys


import curses


class FloatingGrade(Floating):
    def __init__(self, task: Task, _align=""):
        super().__init__(_align)
        self._task = task
        self._line = 0
        self.set_text_ljust()
        self._frame.set_border_color("g")
        self.set_header_text(Text.format("{y/}", " Utilize os direcionais para  marcar "))
        self.set_footer_text(Text.format("{y/}", " Pressione Enter para confirmar "))

        self.grades_index = [task.coverage // 10, task.approach, task.autonomy]
        self.coverage = ["x", "1", "2", "3", "4", "5", "6", "7", "8", "9", "✓"]
        self.coverage_msg = [
            "Não fiz",
            "Fiz 10%",
            "Fiz 20%",
            "Fiz 30%",
            "Fiz 40%",
            "Fiz 50%",
            "Fiz 60%",
            "Fiz 70%",
            "Fiz 80%",
            "Fiz 90%",
            "Fiz 100%"]
        self.approach = [x.text for x in [symbols.approach_x, symbols.approach_e, symbols.approach_d, symbols.approach_c, symbols.approach_b, symbols.approach_a, symbols.approach_s]]
        self.approach_msg = [
            "Não fiz                                     ",
            "Peguei o código pronto e estudei ele        ",
            "Fiz com ajuda de IA (copilot | gpt | outros)",
            "Fiz seguindo aula, vídeo, colega ou monitor ",
            "(Re)Fiz os códigos com algumas consultas    ",
            "(Re)Fiz sozinho e sem consultar algoritmos  ",
            "Fiz de primeira e sem consultar algoritmos  "
            ]
        self.autonomy = [x.text for x in [symbols.autonomy_x, symbols.autonomy_e, symbols.autonomy_d, symbols.autonomy_c, symbols.autonomy_b, symbols.autonomy_a]]
        self.autonomy_msg = [
            r"Consigo refazer menos de 30% sem consulta",
            r"Consigo refazer ao menos 30% sem consulta",
            r"Consigo refazer ao menos 50% sem consulta",
            r"Consigo refazer ao menos 70% sem consulta",
            r"Consigo refazer ao menos 90% sem consulta",
            r"Consigo refazer 100% sem consulta        "
            ]
        self.grades_value = [self.coverage, self.approach, self.autonomy]
        self.grades_msg = [self.coverage_msg, self.approach_msg, self.autonomy_msg]


    def update_content(self):
        self._content = []
        self._content.append(Text())
        self._content.append(Text().add("   Pontue de acordo com a última fez que você (re)fez a tarefa do zero"))
        self._content.append(Text())

        coverage_question = "Cobertura: Quanto entregou?"
        approach_question = "Abordagem: Como foi feito ?"
        autonomy_question = "Autonomia: Quanto domina  ?"

        coverage_text = Text().add(" ").addf("Y" if self._line == 0 else "", coverage_question).add("  ")
        for i, c in enumerate(self.coverage):
            coverage_text.addf("C" if i == self.grades_index[0] else "", c)
        coverage_text.add("  ").addf("m", self.coverage_msg[self.grades_index[0]])
        self._content.append(coverage_text)
        # self._content.append(Text())
        approach_text = Text().add(" ").addf("Y" if self._line == 1 else "", approach_question).add("  ")
        for i, c in enumerate(self.approach):
            approach_text.addf("G" if i == self.grades_index[1] else "", c).add("")
            if c == "x":
                approach_text.add("  ")
            if c == "A":
                approach_text.add("  ")
            if c == "S":
                approach_text.add(" ")
        
        approach_text.add(" ").addf("m", self.approach_msg[self.grades_index[1]])
        self._content.append(approach_text)
        # self._content.append(Text())
        autonomy_text = Text().add(" ").addf("Y" if self._line == 2 else "", autonomy_question).add("  ")
        for i, c in enumerate(self.autonomy):
            autonomy_text.addf("yW" if i == self.grades_index[2] else "", c).add(" ")
        autonomy_text.add(" ").addf("m", self.autonomy_msg[self.grades_index[2]])
        self._content.append(autonomy_text)
        self._content.append(Text())

    def draw(self):
        self._set_default_header()
        self._set_default_footer()
        self.setup_frame()
        self._frame.draw()
        self.update_content()
        self.write_content()

    def change_task(self):
        self._task.set_coverage(self.grades_index[0] * 10)
        self._task.set_approach(self.grades_index[1])
        self._task.set_autonomy(self.grades_index[2])

    def get_input(self) -> int:
        self.draw()
        key: int = Fmt.getch()
        key = InputManager.fix_cedilha(Fmt.get_screen(), key)
        if key == curses.KEY_UP or key == ord(GuiKeys.up):
            self._line = max(self._line - 1, 0)
        elif key == curses.KEY_DOWN or key == ord(GuiKeys.down):
            self._line = min(self._line + 1, 2)
        elif key == curses.KEY_LEFT or key == ord(GuiKeys.left):
            self.grades_index[self._line] = max(self.grades_index[self._line] - 1, 0)
            self.change_task()
        elif key == curses.KEY_RIGHT or key == ord(GuiKeys.right):
            self.grades_index[self._line] = min(self.grades_index[self._line] + 1, len(self.grades_value[self._line]) - 1)
            self.change_task()
        elif key == ord('\n') or key == curses.KEY_BACKSPACE or key == InputManager.esc:
            self._enable = False
            if self._exit_fn is not None:
                self._exit_fn()
        return -1