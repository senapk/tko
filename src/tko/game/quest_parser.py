from tko.game.quest import Quest
from tko.util.get_md_link import get_md_link
from pathlib import Path

"""
## Quest Title key=@chave tag=nome tag=nome2 requires=@outra factor=valor total=valor threshold=valor
Valores podem ser escondidos com <!-- comment -->

Campos suportados:
    - key=@chave: identificador único da quest
    - tag=nome: nome da habilidade/tópico (pode repetir para múltiplos)
    - requires=@outra: pré-requisito (pode repetir)
    - factor=valor: multiplicador de XP das tasks
    - total=valor: pontuação-alvo para 100% de completude
    - threshold=valor: percentual mínimo para considerar a quest completa
    - lang=valor: extensão relacionada a linguagem de programação (pode repetir)
    - Comentários HTML e crases são ignorados
    - Sintaxe antiga (+skill, !@, etc) ainda suportada por compatibilidade
"""

class QuestParser:
    def __init__(self, source_alias: str):
        self.source_alias = source_alias
        self.quest = Quest()
        self.quest.basic.remote_name = source_alias
        self.line: str = ""
        self.line_num = 0
        self.filename: Path = Path("")

    def finish_quest(self) -> Quest:
        if self.quest.basic.key == "":
            self.quest.basic.key = get_md_link(self.quest.basic.title)
        return self.quest

    def match_full_pattern(self) -> bool:
        if self.line.startswith("## "):
            line = self.line[3:]
        elif self.line.startswith("### "):
            line = self.line[4:]
        else:
            return False

        line = line.replace("<!--", " ").replace("-->", " ").replace("`", " ")
        title = self.process_words(line)
        self.quest.basic.title = title
        return True

    def process_words(self, line: str) -> str:
        words = [tag.strip() for tag in line.split(" ") if tag != ""]

        # key (novo formato)
        for w in words:
            if w.startswith("key="):
                self.quest.basic.key = w[4:]

        # tags (novo formato)
        tags = [w[4:] for w in words if w.startswith("tag=")]
        if tags:
            self.quest.config.tags = {t: 1 for t in tags}

        # requires (novo formato)
        requires = [w[9:] for w in words if w.startswith("requires=")]
        for req_key in requires:
            self.quest.requirements.add_require_key(self.quest.basic.remote_name, req_key)

        # factor (novo formato)
        for w in words:
            if w.startswith("factor="):
                try:
                    multiplier = int(w[7:])
                    if multiplier < 0:
                        multiplier = 1
                    for tag in self.quest.config.tags:
                        self.quest.config.tags[tag] = int(self.quest.config.tags[tag] * multiplier)
                except Exception:
                    pass

        # total (novo formato)
        for w in words:
            if w.startswith("total="):
                try:
                    self.quest.config.total_xp = int(w[6:])
                except Exception:
                    self.quest.config.total_xp = 0

        # threshold (novo formato)
        for w in words:
            if w.startswith("threshold="):
                try:
                    self.quest.config.threshold = int(w[10:])
                except Exception:
                    pass


        # languages (novo formato: lang=nome)
        langs = [w[5:] for w in words if w.startswith("lang=")]
        if langs:
            self.quest.config.languages = list(langs)
        else:
            # suporte legado: =lang
            languages = [t[1:] for t in words if t[0] == "="]
            if languages:
                self.quest.config.languages = list(languages)

        # Suporte legado: @key, +skill, !@, %
        keys = [tag for tag in words if tag[0] == "@"]
        if keys and not self.quest.basic.key:
            self.quest.basic.key = keys[0]

        # skills antigos (+skill)
        skills_legacy = [t[1:] for t in words if t[0] == "+"]
        if skills_legacy and not tags:
            self.quest.config.tags = {s: 1 for s in skills_legacy}

        # percent antigo (%)
        qmin = [t[1:] for t in words if t[0] == "%"]
        if qmin and not any(w.startswith("threshold=") for w in words):
            try:
                self.quest.config.threshold = int(qmin[0])
            except ValueError:
                self.quest.config.threshold = 50

        # active (novo formato)
        for w in words:
            if w.startswith("active="):
                val = w[7:].lower()
                self.quest.config.active = (val == "true" or val == "1")

        # requires antigo (!@)
        required_legacy = [t[1:] for t in words if t[0] == "!"]
        for req_key in required_legacy:
            self.quest.requirements.add_require_key(self.quest.basic.remote_name, req_key)

        # Remove campos já processados para título
        def is_field(w: str) -> bool:
            return (
                w.startswith("key=") or w.startswith("tag=") or w.startswith("requires=") or
                w.startswith("factor=") or w.startswith("total=") or w.startswith("threshold=") or
                w.startswith("active=") or (w[0] in ["@", "%", "=", "+", "!"])
            )
        words_title = [w for w in words if not is_field(w)]
        return " ".join(words_title)

    def parse_quest(self, filename: Path, line: str, line_num: int) -> None | Quest:
        self.line = line
        self.line_num = line_num
        self.filename: Path = filename
        self.quest.source.line = self.line
        self.quest.source.line_number = self.line_num
        self.quest.basic.remote_name = ""

        if self.match_full_pattern():
            return self.finish_quest()

        return None