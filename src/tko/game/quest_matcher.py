from tko.game.quest import Quest


class QuestMatcher:
    KEY = "key="
    TAG = "tag="
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
        self._process_languages(words)
        self._process_active(words)

    def remove_fields_from_title(self, text: str) -> str:
        words = text.split()
        # Remove campos já processados para título
        def is_field(w: str) -> bool:
            return (
                w.startswith(QuestMatcher.KEY) or w.startswith(QuestMatcher.TAG) or
                w.startswith("xpgoal=") or w.startswith("min=") or
                w.startswith(QuestMatcher.ACTIVE) or w.startswith(QuestMatcher.LANG) or
                w.startswith("factor=") or (w[0] in ["@", "%", "=", "+"])
            )
        words_title = [w for w in words if not is_field(w)]
        return " ".join(words_title)

    def get_filled_fields(self) -> list[str]:
        quest = self.quest
        output: list[str] = []
        if quest.basic.key:
            output.append(f"@{quest.basic.key}")
        if quest.game.skill and quest.game.skill != quest.basic.key:
            output.append(f"{QuestMatcher.TAG}{quest.game.skill}")
        for lang in quest.game.languages:
            output.append(f"{QuestMatcher.LANG}{lang}")
        if not quest.game.active:
            output.append(f"{QuestMatcher.ACTIVE}0")
        return output
