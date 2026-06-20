from __future__ import annotations
from tko.i18n.message import Msg
import os

SUPPORTED_LANGUAGES = {"pt-BR", "en"}
_LANGUAGE_ALIASES = {
    "pt": "pt-BR",
    "pt-br": "pt-BR",
    "pt_br": "pt-BR",
    "english": "en",
    "en-us": "en",
    "en_uk": "en",
}

_current_language: str | None = None

def normalize_language(language: str | None) -> str:
    if not language:
        return "pt-BR"
    normalized = language.strip().lower().replace("_", "-")
    normalized = _LANGUAGE_ALIASES.get(normalized, normalized)
    if normalized in {"pt", "pt-br"}:
        return "pt-BR"
    if normalized in {"en", "en-us", "en-uk"}:
        return "en"
    if normalized in SUPPORTED_LANGUAGES:
        return normalized
    return "pt-BR"


def get_language() -> str:
    if _current_language is not None:
        return _current_language
    env_language = os.environ.get("TKO_LANG")
    return normalize_language(env_language)


def set_language(language: str | None) -> str:
    global _current_language
    _current_language = normalize_language(language)
    return _current_language

__all__ = ["Msg", "normalize_language", "get_language", "set_language",  "SUPPORTED_LANGUAGES"]
