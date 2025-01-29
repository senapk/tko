from typing import Dict
from tko.util.text import Text, Token
from tko.util.symbols import symbols

class GradeMessage:
    def __init__(self):
        
        self.msg = r"""
           │Compreensão→│Superficial│  Básico   │ Funcional │  Profundo 
↓Autonomia │   Não Fiz  │$1 Confuso  │$2 Inseguro │ $3 Capaz   │$4 Confiante
───────────┼────────────┼───────────┼───────────┼───────────┼────────────
Tutorial   │$8  Guiado   │    [1]    │    [2]    │    [5]    │           
Muita Ajuda│$7  Códigos  │           │    [3]    │    [6]    │           
Pouca Ajuda│$6  Dicas    │           │    [4]    │    [7]    │    [9]    
Sem   Ajuda│$5  Sozinho  │           │           │    [8]    │    [10]   
"""[1:-1]
        
        self.emoji: Dict[str, Token] = {
            "$1": symbols.skill_d,
            "$2": symbols.skill_c,
            "$3": symbols.skill_b,
            "$4": symbols.skill_a,
            "$5": symbols.autonomy_a,
            "$6": symbols.autonomy_b,
            "$7": symbols.autonomy_c,
            "$8": symbols.autonomy_d
        }

        self.axes: Dict[int, list[str]] = {}
        self.load_axes()

    @staticmethod
    def autonomy_emoji(value):
         return [symbols.autonomy_x,
                 symbols.autonomy_e, 
                 symbols.autonomy_d,
                 symbols.autonomy_c,
                 symbols.autonomy_b,
                 symbols.autonomy_a][value]

    @staticmethod
    def skill_emoji(value):
         return [symbols.skill_x,
                 symbols.skill_e, 
                 symbols.skill_d,
                 symbols.skill_c,
                 symbols.skill_b,
                 symbols.skill_a][value]

    @staticmethod
    def grade_to_emojis(grade: int) -> Text:
        decode_dict = {
                0: (symbols.autonomy_e, symbols.skill_e),
                1: (symbols.autonomy_d, symbols.skill_d),
                2: (symbols.autonomy_d, symbols.skill_c),
                3: (symbols.autonomy_c, symbols.skill_c),
                4: (symbols.autonomy_b, symbols.skill_c),
                5: (symbols.autonomy_d, symbols.skill_b),
                6: (symbols.autonomy_c, symbols.skill_b),
                7: (symbols.autonomy_b, symbols.skill_b),
                8: (symbols.autonomy_a, symbols.skill_b),
                9: (symbols.autonomy_b, symbols.skill_a),
                10: (symbols.autonomy_a, symbols.skill_a)
        }
        a = decode_dict[grade][0]
        b = decode_dict[grade][1]
        return Text.format("{} {}", a, b)

    def load_axes(self):
            sozinho = "Sozinho"
            dicas   = "Dicas  "
            codigos = "Códigos"
            guiado  = "Guiado "
            
            superficial = "Superficial"
            basico = "  Básico   "
            funcional = " Funcional "
            profundo = "  Profundo "

            sem_ajuda   = "Sem   Ajuda"
            pouca_ajuda = "Pouca Ajuda"
            muita_ajuda = "Muita Ajuda"
            tutorial    = "Tutorial   "

            confuso   = "Confuso "
            inseguro  = "Inseguro"
            capaz     = "Capaz  "
            confiante = "Confiante"

            self.axes = {
                1: [tutorial, guiado, superficial, confuso],
                2: [tutorial, guiado, basico, inseguro],
                3: [muita_ajuda, codigos, basico, inseguro],
                4: [pouca_ajuda, dicas, basico, inseguro],
                5: [tutorial, guiado, funcional, capaz],
                6: [muita_ajuda, codigos, funcional, capaz],
                7: [pouca_ajuda, dicas, funcional, capaz],
                8: [sem_ajuda, sozinho, funcional, capaz],
                9: [pouca_ajuda, dicas, profundo, confiante],
                10: [sem_ajuda, sozinho, profundo, confiante]
            }

    def format(self, grade: int):
            # pintando compreensão e autonomia
            headers = [Token("Compreensão→", "B"), Token("↓Autonomia ", "M")]
            value: Text = Text().add(self.msg)
            # if grade != 0:
            for h in headers:
                value = value.replace(h.text, h)

            # marcando números com verde
            for i in range (1, 11):
                info = str(i)
                pos = value.get_text().find("    [{}] ".format(info))
                if pos != -1:
                        value.data[pos + 5].text = ' ' # remove number
                        value.data[pos + 6].text = ']' # fix 10
                        value.data[pos + 7].text = ' ' # fix 10
                        if i == grade:
                            value.data[pos + 5].text = 'X'
                            value.data[pos + 7].text = ' '
                            value.data[pos + 4].fmt = "G"
                            value.data[pos + 5].fmt = "G"
                            value.data[pos + 6].fmt = "G"
                        # pos += 1
            
            pos = value.get_text().find("Não Fiz")
            value.data[pos - 3] = symbols.autonomy_e
            value.data[pos - 2] = symbols.skill_e
            # marcando axes com a cor correspondente
            if grade > 0 and grade <= 10:
                value = value.replace(self.axes[grade][0], Token(self.axes[grade][0], "M"))
                value = value.replace(self.axes[grade][1], Token(self.axes[grade][1], "g"))
                value = value.replace(self.axes[grade][2], Token(self.axes[grade][2], "B"))
                value = value.replace(self.axes[grade][3], Token(self.axes[grade][3], "g"))
            # marcando "Não Fiz" com a cor correspondente
            elif grade == 0:
                value = value.replace("Não Fiz", Token("Não Fiz", "R"))

            # inserindo emojis
            for k, v in self.emoji.items():
                value = value.replace(k, v)

            return value
    
