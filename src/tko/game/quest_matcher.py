from tko.game.quest import Quest


class QuestMatcher:
    KEY = "key="
    TAG = "tag="
    REQUIRES = "deps="
    GOAL = "xpgoal="
    MIN = "min="
    LANG = "lang="
    ACTIVE = "active="

    def __init__(self, quest: Quest):
        self.warnings: list[str] = []
        self.quest = quest

    def _process_key(self, words: list[str]):
        # key (novo formato)
        for w in words:
            if w.startswith(QuestMatcher.KEY):
                self.quest.basic.key = w[len(QuestMatcher.KEY):]

        # key (legacy)
        keys = [tag for tag in words if tag[0] == "@"]
        if keys and not self.quest.basic.key:
            self.quest.basic.key = keys[0]

    def _process_skills(self, words: list[str]):
        tags = [w[len(QuestMatcher.TAG):] for w in words if w.startswith(QuestMatcher.TAG)]
        if tags:
            for t in tags:
                for x in t.split(","):
                    self.quest.game.skill = x

        if not self.quest.game.skill and self.quest.basic.key:
            self.quest.game.skill = self.quest.basic.key

    def _process_deps(self, words: list[str]):
        requires = [w[len(QuestMatcher.REQUIRES):] for w in words if w.startswith(QuestMatcher.REQUIRES)]
        for req_key in requires:
            for req in req_key.split(","):
                if req.lower() != "none":
                    self.quest.requirements.add_require_key(self.quest.basic.remote_name, req)

        required_legacy = [t[1:] for t in words if t[0] == "!"]
        for req_key in required_legacy:
            self.quest.requirements.add_require_key(self.quest.basic.remote_name, req_key)

    def _process_goal(self, words: list[str]):
        for w in words:
            if w.startswith(QuestMatcher.GOAL):
                try:
                    w = w[len(QuestMatcher.GOAL):]
                    if w.endswith("xp"):
                        w = w[:-2]
                    self.quest.game.goal_xp = int(w)
                except Exception:
                    self.warnings.append(f"Valor de goal inválido na linha {self.quest.source.line_number} do arquivo {self.quest.source.file}: {w[len(QuestMatcher.GOAL):]}. Usando valor 0.")
                    self.quest.game.goal_xp = 0

    def _process_min(self, words: list[str]):
         # threshold (novo formato)
        for w in words:
            if w.startswith(QuestMatcher.MIN):
                try:
                    w = w[len(QuestMatcher.MIN):]
                    if w.endswith("%"):
                        w = w[:-1]
                    value = int(w)
                    if value < 0 or value > 100:
                        self.warnings.append(f"Valor de threshold fora do intervalo (0-100) na linha {self.quest.source.line_number} do arquivo {self.quest.source.file}: {value}. Usando valor 0.")
                        value = 0
                    self.quest.game.threshold = value
                except Exception:
                    self.warnings.append(f"Valor de threshold inválido na linha {self.quest.source.line_number} do arquivo {self.quest.source.file}: {w[len(QuestMatcher.MIN):]}. Usando valor 0.")
                    self.quest.game.threshold = 0

        # percent antigo (%)
        qmin = [t[1:] for t in words if t[0] == "%"]
        if qmin and not any(w.startswith(QuestMatcher.MIN) for w in words):
            try:
                self.quest.game.threshold = int(qmin[0])
            except ValueError:
                pass

    def _process_languages(self, words: list[str]):
        # languages (novo formato: lang=nome)
        langs = [w[len(QuestMatcher.LANG):] for w in words if w.startswith(QuestMatcher.LANG)]
        if langs:
            self.quest.game.languages = set(langs)
        else:
            # suporte legado: =lang
            languages = [t[1:] for t in words if t[0] == "="]
            if languages:
                self.quest.game.languages = set(languages)

    def _process_active(self, words: list[str]):
        # active (novo formato)
        for w in words:
            if w.startswith(QuestMatcher.ACTIVE):
                val = w[len(QuestMatcher.ACTIVE):].lower()
                self.quest.game.active = (val.lower() == "true" or val == "1" or val.lower() == "yes")
                if val not in ["true", "1", "false", "0"]:
                    self.warnings.append(f"Valor de active inválido na linha {self.quest.source.line_number} do arquivo {self.quest.source.file}: {val}. Usando valor False.")

    def process_fields(self, text: str):
        words = text.split()
        self._process_key(words)
        self._process_skills(words)
        self._process_deps(words)
        self._process_goal(words)
        self._process_min(words)
        self._process_languages(words)
        self._process_active(words)

    def remove_fields_from_title(self, text: str) -> str:
        words = text.split()
        # Remove campos já processados para título
        def is_field(w: str) -> bool:
            return (
                w.startswith(QuestMatcher.KEY) or w.startswith(QuestMatcher.TAG) or w.startswith(QuestMatcher.REQUIRES) or
                w.startswith(QuestMatcher.GOAL) or w.startswith(QuestMatcher.MIN) or
                w.startswith(QuestMatcher.ACTIVE) or w.startswith(QuestMatcher.LANG) or
                w.startswith("factor=") or (w[0] in ["@", "%", "=", "+", "!"])
            )
        words_title = [w for w in words if not is_field(w)]
        return " ".join(words_title)

    def get_filled_fields(self) -> list[str]:
        quest = self.quest
        output: list[str] = []
        if quest.basic.key:
            output.append(f"@{quest.basic.key}")
        if quest.requirements.requires:
            output.append(f"{QuestMatcher.REQUIRES}{','.join(quest.requirements.requires)}")
        if quest.game.skill and quest.game.skill != quest.basic.key:
            output.append(f"{QuestMatcher.TAG}{quest.game.skill}")
        if quest.game.goal_xp > 0:
            output.append(f"{QuestMatcher.GOAL}{quest.game.goal_xp}")
        threshold = quest.game.threshold
        if threshold != quest.game.DEFAULT_MIN:
            output.append(f"{QuestMatcher.MIN}{quest.game.threshold}%")
        for lang in quest.game.languages:
            output.append(f"{QuestMatcher.LANG}{lang}")
        if not quest.game.active:
            output.append(f"{QuestMatcher.ACTIVE}0")
        return output