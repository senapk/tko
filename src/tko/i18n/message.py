from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Msg:
    pt: str
    en: str

    def for_language(self, language: str) -> str:
        return self.pt if language == "pt-BR" else self.en

    def __str__(self) -> str:
        from tko.i18n import get_language

        return self.for_language(get_language())