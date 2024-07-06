from typing import List, Dict, Tuple, Optional
from .quest import Quest
from .game import Game
import subprocess


class Graph:

    colorlist: List[Tuple[str, str]] = [
            ("aquamarine3", "aquamarine4"),
            ("bisque3", "bisque4"),
            ("brown3", "brown4"),
            ("chartreuse3", "chartreuse4"),
            ("coral3", "coral4"),
            ("cyan3", "cyan4"),
            ("darkgoldenrod3", "darkgoldenrod4"),
            ("darkolivegreen3", "darkolivegreen4"),
            ("darkorchid3", "darkorchid4"),
            ("darkseagreen3", "darkseagreen4"),
            ("darkslategray3", "darkslategray4"),
            ("deeppink3", "deeppink4"),
            ("deepskyblue3", "deepskyblue4"),
            ("dodgerblue3", "dodgerblue4"),
            ("firebrick3", "firebrick4"),
            ("gold3", "gold4"),
            ("green3", "green4"),
            ("hotpink3", "hotpink4"),
            ("indianred3", "indianred4"),
            ("khaki3", "khaki4"),
            ("lightblue3", "lightblue4"),
            ("lightcoral", "lightcoral"),
            ("lightcyan3", "lightcyan4"),
            ("lightgoldenrod3", "lightgoldenrod4"),
            ("lightgreen", "lightgreen"),
            ("lightpink3", "lightpink4"),
            ("lightsalmon3", "lightsalmon4"),
            ("lightseagreen", "lightseagreen"),
            ("lightskyblue3", "lightskyblue4"),
            ("lightsteelblue3", "lightsteelblue4"),
            ("lightyellow3", "lightyellow4"),
            ("magenta3", "magenta4"),
            ("maroon3", "maroon4"),
            ("mediumorchid3", "mediumorchid4"),
            ("mediumpurple3", "mediumpurple4"),
            ("mediumspringgreen", "mediumspringgreen"),
            ("mediumturquoise", "mediumturquoise"),
            ("mediumvioletred", "mediumvioletred"),
            ("mistyrose3", "mistyrose4"),
            ("navajowhite3", "navajowhite4"),
            ("olivedrab3", "olivedrab4"),
            ("orange3", "orange4"),
            ("orangered3", "orangered4"),
            ("orchid3", "orchid4"),
            ("palegreen3", "palegreen4"),
            ("paleturquoise3", "paleturquoise4"),
            ("palevioletred3", "palevioletred4")
            ]

    def __init__(self, game: Game):
        self.game = game
        self.reachable: Optional[List[str]] = None
        self.counts: Optional[Dict[str, str]] = None
        self.graph_ext = ".png"
        self.output = "graph"
        self.opt = False

    def set_opt(self, opt: bool):
        self.opt = opt
        return self

    def set_reachable(self, reachable: List[str]):
        self.reachable = reachable
        return self

    def set_counts(self, counts: Dict[str, str]):
        self.counts = counts
        return self

    def set_graph_ext(self, graph_ext: str):
        self.graph_ext = graph_ext
        return self
    
    def set_output(self, output: str):
        self.output = output
        return self

    def info(self, qx: Quest):
        text = f'{qx.title.strip()}'
        if self.reachable is None or self.counts is None:
            return f'"{text}"'
        return f'"{text}\\n{self.counts[qx.key]}"'

    def is_reachable_or_next(self, q: Quest):
        if self.reachable is None:
            return True
        if q.key in self.reachable:
            return True
        for r in q.requires_ptr:
            if r.key in self.reachable:
                return True
        return False

    def generate(self):
        saida = ["digraph diag {", '  node [penwidth=1, style="rounded,filled", shape=box]']

        targets = [q for q in self.game.quests.values() if self.is_reachable_or_next(q)]
        for q in targets:
            token = "->"
            if len(q.requires_ptr) > 0:
                for r in q.requires_ptr:
                    extra = ""
                    if self.reachable is not None:
                        if q.key not in self.reachable and not r.is_complete():
                            extra = "[style=dotted]"
                    saida.append(f"  {self.info(r)} {token} {self.info(q)} {extra}")
            else:
                v = '  "Início"'
                saida.append(f"{v} {token} {self.info(q)}")

        for i, c in enumerate(self.game.clusters):
            cluster_targets = [q for q in c.quests if self.is_reachable_or_next(q)]
            for q in cluster_targets:
                if self.opt:
                    if q.opt:
                        fillcolor = "pink"
                    else:
                        fillcolor = "lime"
                else:
                    if c.color is not None:
                        fillcolor = c.color
                    else:
                        fillcolor = self.colorlist[i][0]

                    if q.opt:
                        fillcolor = f'"{fillcolor};0.9:orange"'
                    else:
                        fillcolor = f'"{fillcolor};0.9:lime"'
                shape = "ellipse"
                color = "black"
                width = 1
                if self.reachable is not None:
                    if q.key not in self.reachable:
                        color = "white"
                    else:
                        width = 3
                        color = q.get_grade_color()
                        if color == "g":
                            color = "green"
                        elif color == "r":
                            color = "red"
                        elif color == "y":
                            color = "yellow"
                        elif color == "m":
                            color = "magenta"
                saida.append(f"  {self.info(q)} [shape={shape} color={color} penwidth={width} fillcolor={fillcolor} ]")

        saida.append("}")
        # saida.append("@enduml")
        saida.append("")

        dot_file = self.output + ".dot"
        out_file = self.output + self.graph_ext
        open(dot_file, "w").write("\n".join(saida))

        if self.graph_ext == ".png":
            subprocess.run(["dot", "-Tpng", dot_file, "-o", out_file])
        elif self.graph_ext == ".svg":
            subprocess.run(["dot", "-Tsvg", dot_file, "-o", out_file])
        else:
            print("Formato de imagem não suportado")
