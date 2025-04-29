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
        self._line = 0
        self.set_text_ljust()
        self._frame.set_border_color("g")
        self.set_header_text(Text.format("{y/}", " Utilize os direcionais e teclas - e + para  marcar "))
        self.set_footer_text(Text.format("{y/}", " Pressione Enter para confirmar "))

        self.grades_index = [task.coverage // 10, task.approach, task.autonomy, task.description, task.desire, task.effort]
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
            Text().addf("y", "(Re)Fiz sozinho").addf("m", " sem consultar algoritmos"),
            Text().addf("y", "Fiz de primeira").addf("m", " sem consultar algoritmos")
            ]
        self.autonomy = [x.text for x in [symbols.autonomy_x, symbols.autonomy_e, symbols.autonomy_d, symbols.autonomy_c, symbols.autonomy_b, symbols.autonomy_a]]
        self.autonomy_msg = [
            Text().addf("m", "Não fiz        ").addf("y", "                         "),
            Text().addf("m", "Consigo refazer ").addf("y", ">= 30% sem consulta      "),
            Text().addf("m", "Consigo refazer ").addf("y", ">= 50% sem consulta      "),
            Text().addf("m", "Consigo refazer ").addf("y", ">= 70% sem consulta      "),
            Text().addf("m", "Consigo refazer ").addf("y", ">= 90% sem consulta      "),
            Text().addf("m", "Consigo refazer ").addf("y", "  100% sem consulta      ")
            ]

        self.description = [x.text for x in [symbols.desire_x, 
                                             symbols.desire_e, 
                                             symbols.desire_d, 
                                             symbols.desire_c, 
                                             symbols.desire_b, 
                                             symbols.desire_a]]
 
        self.description_msg = [
            Text().addf("m", "Sem opinião               "),
            Text().addf("m", "A descrição da atividades ").addf("y", "é confusa     "),
            Text().addf("m", "A descrição da atividades ").addf("y", "é insuficiente"),
            Text().addf("m", "A descrição da atividades ").addf("y", "é razoável    "),
            Text().addf("m", "A descrição da atividades ").addf("y", "é adequada    "),
            Text().addf("m", "A descrição da atividades ").addf("y", "é excelente   ")
            ]
        
       
        self.desire = [x for x in self.description]
        self.desire_msg = [
            Text().addf("m", "Sem opinião        ").addf("y", "                     "),
            Text().addf("m", "A atividade parece ").addf("y", "muito desinteressante"),
            Text().addf("m", "A atividade parece ").addf("y", "desinteressante      "),
            Text().addf("m", "A atividade parece ").addf("y", "indiferente          "),
            Text().addf("m", "A atividade parece ").addf("y", "interessante         "),
            Text().addf("m", "A atividade parece ").addf("y", "muito interessante   "),
            ]

        self.effort = [x for x in self.description]
        self.effort_msg = [
            Text().addf("m", "Sem opinião          ").addf("y", "                   "),
            Text().addf("m", "Resolver a atividade ").addf("y", "foi muito difícil  "),
            Text().addf("m", "Resolver a atividade ").addf("y", "foi difícil        "),
            Text().addf("m", "Resolver a atividade ").addf("y", "foi razoável       "),
            Text().addf("m", "Resolver a atividade ").addf("y", "foi fácil          "),
            Text().addf("m", "Resolver a atividade ").addf("y", "foi muito fácil    "),
            ]

        self.grades_value = [self.coverage, self.approach, self.autonomy, self.description, self.desire, self.effort]
        self.grades_msg = [self.coverage_msg, self.approach_msg, self.autonomy_msg, self.description_msg, self.desire_msg, self.effort_msg]


    def update_content(self):
        self._content = []
        self._content.append(Text())
        self._content.append(Text().add(" ======= Pontue de acordo com a última fez que você (re)fez a tarefa do zero ======="))
        self._content.append(Text().add(" ---------------------------------- Obrigatório ------------------------------------"))
        coverage_question = "Cobertura: Quanto entregou?"
        approach_question = "Abordagem: Como foi feito ?"
        autonomy_question = "Autonomia: Quanto domina  ?"
        description_question = "Descrição: É bem escrita  ?"
        desire_question   = "Interesse: É interessante ?"
        effort_question   = "Dedicação: É fácil        ?"

        coverage_text = Text().add(" ").addf("Y" if self._line == 0 else "", coverage_question).add("  ")
        for i, c in enumerate(self.coverage):
            coverage_text.addf("C" if i == self.grades_index[0] else "", c)
        coverage_text.add("  ").add(self.coverage_msg[self.grades_index[0]])
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
        
        approach_text.add(" ").add(self.approach_msg[self.grades_index[1]])
        self._content.append(approach_text)
        # self._content.append(Text())
        autonomy_text = Text().add(" ").addf("Y" if self._line == 2 else "", autonomy_question).add("  ")
        for i, c in enumerate(self.autonomy):
            autonomy_text.addf("yW" if i == self.grades_index[2] else "", c).add(" ")
        autonomy_text.add(" ").add(self.autonomy_msg[self.grades_index[2]])
        self._content.append(autonomy_text)

        self._content.append(Text().add(" ------------------------------------ Opcional -------------------------------------"))

        description_text = Text().add(" ").addf("Y" if self._line == 3 else "", description_question).add("  ")
        for i, c in enumerate(self.description):
            description_text.addf("yW" if i == self.grades_index[3] else "", c).add(" ")
        description_text.add(" ").add(self.description_msg[self.grades_index[3]])
        self._content.append(description_text)

        desire_text = Text().add(" ").addf("Y" if self._line == 4 else "", desire_question).add("  ")
        for i, c in enumerate(self.desire):
            desire_text.addf("yW" if i == self.grades_index[4] else "", c).add(" ")
        desire_text.add(" ").add(self.desire_msg[self.grades_index[4]])
        self._content.append(desire_text)

        effort_text = Text().add(" ").addf("Y" if self._line == 5 else "", effort_question).add("  ")
        for i, c in enumerate(self.effort):
            effort_text.addf("yW" if i == self.grades_index[5] else "", c).add(" ")
        effort_text.add(" ").add(self.effort_msg[self.grades_index[5]])
        self._content.append(effort_text)

        self._content.append(Text())

    # @override
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
        self._task.set_description(self.grades_index[3])
        self._task.set_desire(self.grades_index[4])
        self._task.set_effort(self.grades_index[5])

    # @override
    def get_input(self) -> int:
        self.draw()
        key: int = Fmt.getch()
        key = InputManager.fix_cedilha(Fmt.get_screen(), key)
        if key == self.settings.app.get_key_up() or key == ord(GuiKeys.up) or key == ord(GuiKeys.up2):
            self._line = max(self._line - 1, 0)
        elif key == self.settings.app.get_key_down() or key == ord(GuiKeys.down) or key == ord(GuiKeys.down2):
            self._line = min(self._line + 1, len(self.grades_index) - 1)
        elif key == self.settings.app.get_key_left() or key == ord(GuiKeys.left) or key == ord(GuiKeys.left2):
            self.grades_index[self._line] = max(self.grades_index[self._line] - 1, 0)
            self.change_task()
        elif key == self.settings.app.get_key_right() or key == ord(GuiKeys.right) or key == ord(GuiKeys.right2):
            self.grades_index[self._line] = min(self.grades_index[self._line] + 1, len(self.grades_value[self._line]) - 1)
            self.change_task()
        elif key == ord("0"):
            for i in range(len(self.grades_index)):
                self.grades_index[i] = len(self.grades_value[i]) - 1
        elif key == ord("-"):
            for i in range(len(self.grades_index)):
                self.grades_index[i] = max(self.grades_index[i] - 1, 0)
        elif key == ord("+") or key == ord("="):
            for i in range(len(self.grades_index)):
                self.grades_index[i] = min(self.grades_index[i] + 1, len(self.grades_value[i]) - 1)
        elif key == ord('\n') or key == curses.KEY_BACKSPACE or key == InputManager.esc:
            self._enable = False
            if self._exit_fn is not None:
                self._exit_fn()
        return -1