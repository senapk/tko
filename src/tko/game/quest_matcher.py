from tko.game.quest import Quest


class QuestMatcher:
    KEY = "key="
    SKILL = "skills="
    REQUIRES = "deps="
    FACTOR = "factor="
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
        tags = [w[len(QuestMatcher.SKILL):] for w in words if w.startswith(QuestMatcher.SKILL)]
        if tags:
            for t in tags:
                for x in t.split(","):
                    self.quest.config.skills.add(x)
        else:
            # skills antigos (+skill)
            skills_legacy = [t[1:] for t in words if t[0] == "+"]
            for sk in skills_legacy:
                if ":" in sk:
                    skill_name, skill_value = sk.split(":", 1)
                    try:
                        self.quest.config.factor = int(skill_value)
                    except ValueError:
                        self.warnings.append(f"Valor de skill inválido para {skill_name} na linha {self.quest.source.line_number} do arquivo {self.quest.source.file}: {skill_value}. Usando valor 1.")
                    self.quest.config.skills.add(skill_name)

        if not self.quest.config.skills and self.quest.basic.key:
            self.quest.config.skills = {self.quest.basic.key}

    def _process_deps(self, words: list[str]):
        requires = [w[len(QuestMatcher.REQUIRES):] for w in words if w.startswith(QuestMatcher.REQUIRES)]
        for req_key in requires:
            for req in req_key.split(","):
                if req.lower() != "none":
                    self.quest.requirements.add_require_key(self.quest.basic.remote_name, req)

        required_legacy = [t[1:] for t in words if t[0] == "!"]
        for req_key in required_legacy:
            self.quest.requirements.add_require_key(self.quest.basic.remote_name, req_key)

    def _process_factor(self, words: list[str]):
        # factor (novo formato)
        for w in words:
            if w.startswith(QuestMatcher.FACTOR):
                try:
                    multiplier = int(w[len(QuestMatcher.FACTOR):])
                    self.quest.config.factor = multiplier
                except Exception:
                    self.warnings.append(f"Valor de factor inválido na linha {self.quest.source.line_number} do arquivo {self.quest.source.file}: {w[len(QuestMatcher.FACTOR):]}. Ignorando factor.")

    def _process_goal(self, words: list[str]):
        for w in words:
            if w.startswith(QuestMatcher.GOAL):
                try:
                    w = w[len(QuestMatcher.GOAL):]
                    if w.endswith("xp"):
                        w = w[:-2]
                    self.quest.config.goal_xp = int(w)
                except Exception:
                    self.warnings.append(f"Valor de goal inválido na linha {self.quest.source.line_number} do arquivo {self.quest.source.file}: {w[len(QuestMatcher.GOAL):]}. Usando valor 0.")
                    self.quest.config.goal_xp = 0

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
                    self.quest.config.threshold = value
                except Exception:
                    self.warnings.append(f"Valor de threshold inválido na linha {self.quest.source.line_number} do arquivo {self.quest.source.file}: {w[len(QuestMatcher.MIN):]}. Usando valor 0.")
                    self.quest.config.threshold = 0

        # percent antigo (%)
        qmin = [t[1:] for t in words if t[0] == "%"]
        if qmin and not any(w.startswith(QuestMatcher.MIN) for w in words):
            try:
                self.quest.config.threshold = int(qmin[0])
            except ValueError:
                pass

    def _process_languages(self, words: list[str]):
        # languages (novo formato: lang=nome)
        langs = [w[len(QuestMatcher.LANG):] for w in words if w.startswith(QuestMatcher.LANG)]
        if langs:
            self.quest.config.languages = set(langs)
        else:
            # suporte legado: =lang
            languages = [t[1:] for t in words if t[0] == "="]
            if languages:
                self.quest.config.languages = set(languages)

    def _process_active(self, words: list[str]):
        # active (novo formato)
        for w in words:
            if w.startswith(QuestMatcher.ACTIVE):
                val = w[len(QuestMatcher.ACTIVE):].lower()
                self.quest.config.active = (val.lower() == "true" or val == "1" or val.lower() == "yes")
                if val not in ["true", "1", "false", "0"]:
                    self.warnings.append(f"Valor de active inválido na linha {self.quest.source.line_number} do arquivo {self.quest.source.file}: {val}. Usando valor False.")

    def process_fields(self, text: str):
        words = text.split()
        self._process_key(words)
        self._process_skills(words)
        self._process_deps(words)
        self._process_factor(words)
        self._process_goal(words)
        self._process_min(words)
        self._process_languages(words)
        self._process_active(words)

    def remove_fields_from_title(self, text: str) -> str:
        words = text.split()
        # Remove campos já processados para título
        def is_field(w: str) -> bool:
            return (
                w.startswith(QuestMatcher.KEY) or w.startswith(QuestMatcher.SKILL) or w.startswith(QuestMatcher.REQUIRES) or
                w.startswith(QuestMatcher.FACTOR) or w.startswith(QuestMatcher.GOAL) or w.startswith(QuestMatcher.MIN) or
                w.startswith(QuestMatcher.ACTIVE) or (w[0] in ["@", "%", "=", "+", "!"])
            )
        words_title = [w for w in words if not is_field(w)]
        return " ".join(words_title)

    def get_filled_fields(self) -> list[str]:
        quest = self.quest
        output: list[str] = []
        output.append(f"@{quest.basic.key}")
        if quest.requirements.requires:
            output.append(f"{QuestMatcher.REQUIRES}{",".join(quest.requirements.requires)}")
        else:
            output.append(f"{QuestMatcher.REQUIRES}none")
        for skill in quest.config.skills:
            if skill == quest.basic.key:
                continue
            output.append(f"{QuestMatcher.SKILL}{skill}")
        factor :int | float = quest.config.factor
        if int(factor) == factor:
            factor = int(factor)
        output.append(f"{QuestMatcher.FACTOR}{factor}")
        output.append(f"{QuestMatcher.GOAL}{quest.config.goal_xp}")
        threshold = quest.config.threshold
        if threshold != quest.config.DEFAULT_MIN:
            output.append(f"{QuestMatcher.MIN}{quest.config.threshold}%")
        for lang in quest.config.languages:
            output.append(f"{QuestMatcher.LANG}{lang}")
        output.append(f"{QuestMatcher.ACTIVE}{"1" if quest.config.active else "0"}")
        return output