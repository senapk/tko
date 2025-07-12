from tko.game.task import Task
from tko.play.floating import Floating
from tko.play.fmt import Fmt
from tko.play.input_manager import InputManager
from tko.util.symbols import symbols
from tko.util.text import Text
from tko.play.keys import GuiKeys
from tko.settings.settings import Settings
from tko.game.task_grader import TaskGrader
# from typing import override

import curses


class FloatingGrade(Floating):
    def __init__(self, task: Task, settings: Settings, _align: str =""):
        super().__init__(settings, _align)
        self.settings = settings
        self._task = task
        self._grader = TaskGrader(task.info)
        self._line = 0 if not task.is_leet() else 1
        self.set_text_ljust()
        self._frame.set_border_color("g")
        self.set_header_text(Text.format("{y/}", " Utilize os direcionais e teclas - e + para  marcar "))
        self.set_footer_text(Text.format("{y/}", " Pressione Enter para confirmar "))

        self.grades_index = [task.info.rate // 10, task.info.flow, task.info.edge, task.info.neat, task.info.cool, task.info.easy]
        self.rate_opt = ["x", "1", "2", "3", "4", "5", "6", "7", "8", "9", "✓"]
        self.rate_msg = [
            Text().addf("g", "Não ").addf("y", "fiz"),
            Text().addf("y", " 10%"),
            Text().addf("y", " 20%"),
            Text().addf("y", " 30%"),
            Text().addf("y", " 40%"),
            Text().addf("y", " 50%"),
            Text().addf("y", " 60%"),
            Text().addf("y", " 70%"),
            Text().addf("y", " 80%"),
            Text().addf("y", " 90%"),
            Text().addf("y", "100%")]
        self.flow_opt = [x.text for x in [symbols.flow_x, symbols.flow_e, symbols.flow_d, symbols.flow_c, symbols.flow_b, symbols.flow_a, symbols.flow_s]]
        self.flow_msg = [
            Text().addf("g", "Não fiz"),
            Text().addf("g", "Fiz com ajuda ").addf("Y", "H").addf("y", "umana").addf("g", "(colega|monitor|...)"),
            Text().addf("g", "Fiz com ajuda de ").addf("Y", "I").addf("y", "A").addf("g", "(copilot|gpt|...)"),
            Text().addf("g", "Fiz ").addf("Y", "G").addf("y","uiado").addf("g", "/Copiando").addf("g", "(").addf("g", "aula|vídeo").addf("g", "|...)"),
            Text().addf("g", "Fiz ").addf('Y', 'P').addf("y", "esquisando").addf("g", "(livros|sites|youtube|...)"),
            Text().addf("g", "Fiz ").addf("g", "sem consultar ").addf('Y', 'A').addf("y", "lgoritmos"),
            Text().addf("g", "Fiz ").addf("Y", 'S').addf("y", "ozinho").addf("g", " sem consultar nada")
            ]
        self.edge_opt = [x.text for x in [symbols.edge_x, symbols.edge_e, symbols.edge_d, symbols.edge_c, symbols.edge_b, symbols.edge_a]]
        self.edge_msg = [
            Text().addf("g", "Não fiz        ").addf("y", "                         "),
            Text().addf("g", "Consigo refazer ").addf("y", ">= 30% sem consulta     "),
            Text().addf("g", "Consigo refazer ").addf("y", ">= 50% sem consulta     "),
            Text().addf("g", "Consigo refazer ").addf("y", ">= 70% sem consulta     "),
            Text().addf("g", "Consigo refazer ").addf("y", ">= 90% sem consulta     "),
            Text().addf("g", "Consigo refazer ").addf("y", "  100% sem consulta     ")
            ]

        self.neat_opt = [x.text for x in [symbols.cool_x, 
                                             symbols.cool_e, 
                                             symbols.cool_d, 
                                             symbols.cool_c, 
                                             symbols.cool_b, 
                                             symbols.cool_a]]
 
        self.neat_msg = [
            Text().addf("g", "Sem opinião               "),
            Text().addf("g", "A descrição da atividades ").addf("y", "é confusa     "),
            Text().addf("g", "A descrição da atividades ").addf("y", "é insuficiente"),
            Text().addf("g", "A descrição da atividades ").addf("y", "é razoável    "),
            Text().addf("g", "A descrição da atividades ").addf("y", "é adequada    "),
            Text().addf("g", "A descrição da atividades ").addf("y", "é excelente   ")
            ]
        
       
        self.cool_opt = [x for x in self.neat_opt]
        self.cool_msg = [
            Text().addf("g", "Sem opinião        ").addf("y", "                     "),
            Text().addf("g", "A atividade parece ").addf("y", "muito desinteressante"),
            Text().addf("g", "A atividade parece ").addf("y", "desinteressante      "),
            Text().addf("g", "A atividade parece ").addf("y", "indiferente          "),
            Text().addf("g", "A atividade parece ").addf("y", "interessante         "),
            Text().addf("g", "A atividade parece ").addf("y", "muito interessante   "),
            ]

        self.easy_opt = [x for x in self.neat_opt]
        self.easy_msg = [
            Text().addf("g", "Sem opinião          ").addf("y", "                   "),
            Text().addf("g", "Resolver a atividade ").addf("y", "foi muito difícil  "),
            Text().addf("g", "Resolver a atividade ").addf("y", "foi difícil        "),
            Text().addf("g", "Resolver a atividade ").addf("y", "foi razoável       "),
            Text().addf("g", "Resolver a atividade ").addf("y", "foi fácil          "),
            Text().addf("g", "Resolver a atividade ").addf("y", "foi muito fácil    "),
            ]

        self.grades_value = [self.rate_opt, self.flow_opt, self.edge_opt, self.neat_opt, self.cool_opt, self.easy_opt]
        self.grades_msg = [self.rate_msg, self.flow_msg, self.edge_msg, self.neat_msg, self.cool_msg, self.easy_msg]


    def update_content(self):
        self._content = []
        self._content.append(Text().add("         Pontue de acordo com a última fez que você (re)fez a tarefa do zero           "))
        width = 90
        flow_value = self._grader.get_flow_percent()
        edge_value = self._grader.get_edge_percent()
        somatorio = (Text()
                    # .addf('c', f'{self._task.info.get_rate()}%') .add(" * ")
                    # .addf('c', f'{flow_value}%') .add(" * ")
                    # .addf('c', f'{edge_value}%') .add(" = ")
                    .addf('g', f'{round(self._task.get_percent()):>3}%'))

        self._content.append(Text().add("╔") + Text().add(" Tarefa:").add(somatorio).add(" ").center(width, Text.Token("═", "")))
        rate_question = "Cobertura: Quanto entregou?"
        flow_question = "Abordagem: Como foi feito ?"
        edge_question = "Autonomia: Quanto domina  ?"
        neat_question = "Descrição: É bem escrita  ?"
        cool_question = "Interesse: É interessante ?"
        easy_question = "Dedicação: É fácil        ?"

        opening = "╠═ "
        op_prefix = opening if not self._task.is_leet() else "║  "
        rate_text = Text().add(op_prefix).addf("Y" if self._line == 0 else "", rate_question).add("  ")
        for i, c in enumerate(self.rate_opt):
            rate_text.addf("Y" if i == self.grades_index[0] else "", c)
        rate_text.add("  ").add(self.rate_msg[self.grades_index[0]])
        self._content.append(rate_text)
        # self._content.append(Text())
        flow_text = Text().add(opening).addf("Y" if self._line == 1 else "", flow_question).add("  ")
        for i, c in enumerate(self.flow_opt):
            flow_text.addf("Y" if i == self.grades_index[1] else "", c).add("")
            if c == "x":
                flow_text.add("  ")
            if c == "P":
                flow_text.add("  ")
            if c == "S":
                flow_text.add(" ")


        flow_text.add(" ").addf('y', f'{flow_value:>3}% ').add(self.flow_msg[self.grades_index[1]])
        self._content.append(flow_text)
        # self._content.append(Text())

        prefix = opening
        if self.done_alone() or self.not_done():
            prefix = "║  "
        edge_text = Text().add(prefix).addf("Y" if self._line == 2 else "", edge_question).add("  ")
        for i, c in enumerate(self.edge_opt):
            edge_text.addf("y" if i == self.grades_index[2] else "", c).add(" ")

        edge_text.add(" ").addf('y', f'{edge_value:>3}% ')
        # edge_text.add(" ").add(self.edge_msg[self.grades_index[2]])
        self._content.append(edge_text)
        self._content.append(Text().add("╟───────────────────────────────────── Opcional ───────────────────────────────────────────"))

        description_text = Text().add(opening).addf("Y" if self._line == 3 else "", neat_question).add("  ")
        for i, c in enumerate(self.neat_opt):
            description_text.addf("Y" if i == self.grades_index[3] else "", c).add(" ")
        description_text.add(" ").add(self.neat_msg[self.grades_index[3]])
        self._content.append(description_text)

        desire_text = Text().add(opening).addf("Y" if self._line == 4 else "", cool_question).add("  ")
        for i, c in enumerate(self.cool_opt):
            desire_text.addf("Y" if i == self.grades_index[4] else "", c).add(" ")
        desire_text.add(" ").add(self.cool_msg[self.grades_index[4]])
        self._content.append(desire_text)

        effort_text = Text().add(opening).addf("Y" if self._line == 5 else "", easy_question).add("  ")
        for i, c in enumerate(self.easy_opt):
            effort_text.addf("Y" if i == self.grades_index[5] else "", c).add(" ")
        effort_text.add(" ").add(self.easy_msg[self.grades_index[5]])
        self._content.append(effort_text)

        self._content.append(Text().add("╚══════════════════════════════════════════════════════════════════════════════════════════"))

    # @override
    def draw(self):
        self._set_default_header()
        self._set_default_footer()
        self.setup_frame()
        self._frame.draw()
        self.update_content()
        self.write_content()

    def change_task(self):
        if not self._task.is_leet ():
            self._task.info.set_rate(self.grades_index[0] * 10)
        self._task.info.set_flow(self.grades_index[1])
        self._task.info.set_edge(self.grades_index[2])
        self._task.info.set_neat(self.grades_index[3])
        self._task.info.set_cool(self.grades_index[4])
        self._task.info.set_easy(self.grades_index[5])

    def done_alone(self) -> bool:
        return self.grades_index[1] > 4

    def not_done(self) -> bool:
        return self.grades_index[1] == 0
    
    def set_autonomy_max(self):
        self.grades_index[2] = 5


    def send_key_up(self):
        if not(self._task.is_leet() and self._line == 1):
            self._line = max(self._line - 1, 0)
        if (self.done_alone() and self._line == 2) or (self.not_done() and self._line == 2):
            self._line = max(self._line - 1, 0)


    def send_key_down(self):
        self._line = min(self._line + 1, len(self.grades_index) - 1)
        if (self.done_alone() and self._line == 2) or (self.not_done() and self._line == 2):
            self._line = min(self._line + 1, len(self.grades_index) - 1)


    def send_key_left(self):
        self.grades_index[self._line] = max(self.grades_index[self._line] - 1, 0)
        # if self._line == 1 and self.grades_index[1] < 5:
        #     self.grades_index[2] = 0
        if self._line == 1 and self.done_alone() and self.grades_index[self._line] == 5:
            self.set_autonomy_max()
            self.grades_index[2] -= 1
        self.change_task()


    def send_key_right(self):
        self.grades_index[self._line] = min(self.grades_index[self._line] + 1, len(self.grades_value[self._line]) - 1)
        if self._line == 1 and self.done_alone() and self.grades_index[self._line] == 6:
            self.set_autonomy_max()
        if self._line == 1 and self.done_alone() and self.grades_index[self._line] == 5:
            self.set_autonomy_max()
            self.grades_index[2] -= 1
        if self._line == 2 and self.grades_index[1] < 6:
            self.grades_index[2] = min(self.grades_index[2], 4)
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