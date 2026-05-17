from __future__ import annotations

from enum import Enum

class CoreMsgKey(str, Enum):
    APP_CONTEXT_NOT_SET = 'app.context_not_set'
    APP_KEYBOARD_INTERRUPT = 'app.keyboard_interrupt'
    APP_VERSION = 'app.version'
    OPEN_ACTION_HINT = 'open.action_hint'
    OPEN_INVALID_REPO = 'open.invalid_repo'
    RESET_LANGUAGES_PATH = 'reset.languages_path'
    RESET_NO_REPO = 'reset.no_repo'
    RESET_SETTINGS_PATH = 'reset.settings_path'
    UI_LANGUAGE_CHANGED = 'ui.language_changed'
