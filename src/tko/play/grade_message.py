from typing import Dict
from tko.util.text import Text, Token
from tko.util.symbols import symbols

class GradeMessage:
    def __init__(self):
#         self.msg2 = r"""
#   Não Fiz  │Compreensão→│Superficial│    Básico │Funcional │   Profundo 
# ↓Autonomia │            │$1 Confuso  │$2 Inseguro │$3 Capaz   │$4 Confiante
# ───────────┼────────────┼───────────┼───────────┼──────────┼────────────
# Sem   Ajuda│$5  Sozinho  │           │           │   [8]    │    [10]    
# Pouca Ajuda│$6  Dicas    │           │    [4]    │   [7]    │    [9]     
# Muita Ajuda│$7  Códigos  │           │    [3]    │   [6]    │            
# Tutorial   │$8  Guiado   │    [1]    │    [2]    │   [5]    │            
# """[1:-1]
        
        self.msg = r"""
           │Compreensão→│Superficial│  Básico   │ Funcional │  Profundo 
↓Autonomia │  Não Fiz   │$1 Confuso  │$2 Inseguro │ $3 Capaz   │$4 Confiante
───────────┼────────────┼───────────┼───────────┼───────────┼────────────
Tutorial   │$8  Guiado   │    [1]    │    [2]    │    [5]    │           
Muita Ajuda│$7  Códigos  │           │    [3]    │    [6]    │           
Pouca Ajuda│$6  Dicas    │           │    [4]    │    [7]    │    [9]    
Sem   Ajuda│$5  Sozinho  │           │           │    [8]    │    [10]   
"""[1:-1]
        
        self.emoji: Dict[str, Token] = {
            "$1": symbols.emoji_confuso,
            "$2": symbols.emoji_inseguro,
            "$3": symbols.emoji_capaz,
            "$4": symbols.emoji_confiante,
            "$5": symbols.emoji_alone,
            "$6": symbols.emoji_dicas,
            "$7": symbols.emoji_codes,
            "$8": symbols.emoji_guide
        }

        self.axes: Dict[int, list[str]] = {}
        self.load_axes()

    @staticmethod
    def grade_to_emojis(grade: int) -> Text:
        decode_dict = {
                0: (Token("-"), symbols.emoji_nao_fiz),
                1: (symbols.emoji_guide, symbols.emoji_confuso),
                2: (symbols.emoji_guide, symbols.emoji_inseguro),
                3: (symbols.emoji_codes, symbols.emoji_inseguro),
                4: (symbols.emoji_dicas, symbols.emoji_inseguro),
                5: (symbols.emoji_guide, symbols.emoji_capaz),
                6: (symbols.emoji_codes, symbols.emoji_capaz),
                7: (symbols.emoji_dicas, symbols.emoji_capaz),
                8: (symbols.emoji_alone, symbols.emoji_capaz),
                9: (symbols.emoji_dicas, symbols.emoji_confiante),
                10: (symbols.emoji_alone, symbols.emoji_confiante)
        }
        a = decode_dict[grade][0]
        b = decode_dict[grade][1]
        return Text("{} {}", b, a)

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
            value: Text = Text(self.msg)
            if grade != 0:
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
            
            # marcando axes com a cor correspondente
            if grade > 0 and grade <= 10:
                value = value.replace(self.axes[grade][0], Token(self.axes[grade][0], "M"))
                value = value.replace(self.axes[grade][1], Token(self.axes[grade][1], "g"))
                value = value.replace(self.axes[grade][2], Token(self.axes[grade][2], "B"))
                value = value.replace(self.axes[grade][3], Token(self.axes[grade][3], "g"))

                value = value.replace("  Não Fiz  ", Token("           "))

            # marcando "Não Fiz" com a cor correspondente
            elif grade == 0:
                value = value.replace("  Não Fiz   ", Token("  Não Fiz   ", "R"))

            # inserindo emojis
            for k, v in self.emoji.items():
                value = value.replace(k, v)

            return value
    
