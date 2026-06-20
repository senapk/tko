from __future__ import annotations
from dataclasses import dataclass
from tko.util.rt import RT

from dataclasses import dataclass

@dataclass(frozen=True)
class Msg:
    pt: RT
    en: RT

    @staticmethod
    def text(pt: str, en: str) -> Msg:
        return Msg(RT(pt), RT(en))

    @staticmethod
    def parse(pt: str, en: str) -> Msg:
        return Msg(RT.parse(pt), RT.parse(en))
    
    def for_language(self, language: str) -> RT:
        return self.pt if language == "pt-BR" else self.en

    def t(self) -> RT:
        from tko.i18n import get_language
        return self.for_language(get_language())
    
    def __str__(self) -> str:
        return str(self.t())
