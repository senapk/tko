from __future__ import annotations

import os
import re
from typing import Any
from enum import Enum
from tko.i18n.msgkeys import MsgKey


_SUPPORTED_LANGUAGES = {"pt-BR", "en"}
_LANGUAGE_ALIASES = {
    "pt": "pt-BR",
    "pt-br": "pt-BR",
    "pt_br": "pt-BR",
    "english": "en",
    "en-us": "en",
    "en_uk": "en",
}

from tko.i18n.catalogs import TRANSLATIONS as _TRANSLATIONS


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
    env_language = os.environ.get("TKO_LANG") or os.environ.get("LANG") or os.environ.get("LC_ALL")
    return normalize_language(env_language)


def set_language(language: str | None) -> str:
    global _current_language
    _current_language = normalize_language(language)
    return _current_language


def get_catalog_keys(language: str) -> set[str]:
    normalized = normalize_language(language)
    return set(_TRANSLATIONS.get(normalized, _TRANSLATIONS["pt-BR"]).keys())


def t(key: Enum | str, **params: Any) -> str:
    key_value = key.value if isinstance(key, Enum) else key
    language = get_language()
    catalog = _TRANSLATIONS.get(language, _TRANSLATIONS["pt-BR"])
    template = catalog.get(key_value, _TRANSLATIONS["pt-BR"].get(key_value, key_value))

    if not params:
        return template

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in params:
            return str(params[name])
        return match.group(0)

    return re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", replace, template)


__all__ = ["MsgKey", "normalize_language", "get_language", "set_language", "get_catalog_keys", "t"]
