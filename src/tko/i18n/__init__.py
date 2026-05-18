from __future__ import annotations

import os
import re
from enum import Enum
from typing import Any

from tko.i18n.message import Msg


_SUPPORTED_LANGUAGES = {"pt-BR", "en"}
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
    if normalized in _SUPPORTED_LANGUAGES:
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


def t(key: Enum | str | Msg, **params: Any) -> str:
    language = get_language()
    if isinstance(key, Msg):
        template = key.for_language(language)
    else:
        key_value = key.value if isinstance(key, Enum) else key
        template = str(key_value)

    if not params:
        return template

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in params:
            return str(params[name])
        return match.group(0)

    return re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", replace, template)


__all__ = ["Msg", "normalize_language", "get_language", "set_language", "t"]
