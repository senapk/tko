from typing import List, Dict, Any
from tko.util.ftext import FF

class Flag:
    def __init__(self):
        self._name: str = ""
        self._text: str = ""  # description
        self._char: str = ""
        self._values: List[str] = ["0", "1"]
        self._index: int = 0
        self._location: str = ""
        self._bool = True  # many options

    def name(self, _name):
        self._name = _name
        return self

    def text(self, _text):
        self._text = _text
        return self

    def char(self, _key):
        self._char = _key
        return self

    def values(self, _values: List[str]):
        self._values = _values
        return self

    def index(self, _index):
        self._index = _index
        return self

    def location(self, value: str):
        self._location = value
        return self

    def toggle(self):
        self._index = (self._index + 1) % len(self._values)
        return self

    def many(self):
        self._bool = False
        return self
    
    def bool(self):
        self._bool = True
        return self
    
    def is_bool(self):
        return self._bool

    def get_location(self) -> str:
        return self._location

    def get_value(self) -> str:
        return self._values[self._index]

    def is_true(self):
        return self.get_value() == "1"

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return self._text

    def get_char(self) -> str:
        return self._char

    def get_index(self) -> int:
        return self._index

    def get_color(self) -> str:
        if self.get_value() == "1":
            return Flags.flag_on.get_value()
        return Flags.flag_off.get_value()

    def get_toggle_sentence(self, pad: int = 0) -> FF:
        if not self._bool:
            name = FF().addf(self.get_value(), f"{self._name}".ljust(pad))
            value = FF().add(f"[{self.get_char()}]").add(f"{self.get_value()}".rjust(2)).add(" ").add(name)
            return value
            
        char = self.get_char()
        text = self.get_name()
        color = self.get_color()
        extra = FF()
        if pad > 0:
            extra.addf(color, (pad - len(text)) * " ")
        visual = "━─"
        if self.is_true():
            visual = "─━"
        value = FF().add(f"[{char}]").addf(color, f"{visual} ").addf(color + "/", text).add(extra)
        return value
    

class Flags:
    count = Flag().name("Count").char("C").text("Mostra a contagem de tarefas").location("left")
    down = Flag().name("Down").char("D").text("Mostra o caminho para a tarefa baixadas").location("left")
    minimum = Flag().name("Minimum").char("M").text("Mostra a nota mínima para a tarefa").location("left")
    opt = Flag().name("Opt").char("O").text("Mostra tarefas opcionais").location("left")
    xp = Flag().name("Xp").char("X").text("Mostra a xp obtida").location("left")
    percent = Flag().name("Percent").char("P").text("Mostra a porcentagem de tarefas").location("left")
    admin = Flag().name("Admin").char("A").text("Mostra todas as missões e grupos").location("left")

    dots = Flag().name("Dots").char(".").values(["1", "0"]).text("Mostra o preenchimento com pontos").location("left")
    group_prog = Flag().name("Group").values(["1", "0"]).text("Mostra a barra de progresso dos grupos")
    quest_prog = Flag().name("Quest").values(["1", "0"]).text("Mostra a barra de progresso das missões")

    help_bar = Flag().name("HelpBar").char("H").values(["1", "0"]).text("Mostra a barra de ajuda").location("top")
    skills_bar = Flag().name("SkillsBar").char("S").values(["1", "0"]).text("Mostra a barra de skills").location("top")
    flags_bar = Flag().name("FlagsBar").char("F").values(["1", "0"]).text("Mostra a barra de flags").location("top")

    focus     = Flag().name("Focus").char("z").values(["B", "R", "G", "Y", "wK", "kW"]).text("Cor do item em foco").many().location("left")
    prog_done = Flag().name("ProgDone").char("x").values(["g", "b", "c", "k", "w"]).text("Progresso Done").many().location("left")
    prog_todo = Flag().name("ProgTodo").char("c").values(["y", "m", "r", "k", "w"]).text("Progresso Todo").many().location("left")
    flag_on   = Flag().name("FlagTrue").char("v").values(["G", "W", "B", "C", "wK", "kW"]).text("Flag True").many().location("left")
    flag_off  = Flag().name("FlagFalse").char("b").values(["Y", "R", "M", "wK", "kW"]).text("Flag False").many().location("left")
    cmds      = Flag().name("Cmds").char("n").values(["B", "C", "M", "Y", "wK", "kW"]).text("CMDS").many()
    skill_done = Flag().name("SkillDone").char("y").values(["G", "B", "C", "wK", "kW"]).text("Skill Done").many().location("left")
    skill_todo = Flag().name("SkillTodo").char("u").values(["Y", "R", "M", "wK", "kW"]).text("Skill Todo").many().location("left")
    main_done = Flag().name("MainDone").char("i").values(["B", "G", "C", "wK", "kW"]).text("Main Done").many().location("left")
    main_todo = Flag().name("MainTodo").char("p").values(["M", "R", "Y", "wK", "kW"]).text("Main Todo").many().location("left")


class FlagsMan:
    def __init__(self, data: Dict[str, int]):
        self.flags: Dict[str, Flag] = {}
        self.left: List[Flag] = []
        self.top: List[Flag] = []

        for flag in Flags.__dict__.values():
            if isinstance(flag, Flag):
                self.flags[flag.get_name()] = flag
                if flag.get_location() == "left":
                    self.left.append(flag)
                elif flag.get_location() == "top":
                    self.top.append(flag)

        for key, _index in data.items():
            if key in self.flags:
                self.flags[key].index(_index)

    def get_data(self) -> Dict[str, int]:
        data = {}
        for name, flag in self.flags.items():
            data[name] = flag.get_index()
        return data

