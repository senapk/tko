from __future__ import annotations

from enum import Enum

class ConfigMsgKey(str, Enum):
    CONFIG_BORDERS_STATUS = 'config.borders_status'
    CONFIG_DIFF_MODE_DOWN = 'config.diff_mode_down'
    CONFIG_DIFF_MODE_SIDE = 'config.diff_mode_side'
    CONFIG_EDITOR_CHANGED = 'config.editor_changed'
    CONFIG_IMAGES_STATUS = 'config.images_status'
    CONFIG_LANG_EMPTY = 'config.lang_empty'
    CONFIG_LANG_LOAD_FAILED = 'config.lang_load_failed'
    CONFIG_TIMEOUT_CHANGED = 'config.timeout_changed'
    LANG_SELECT_DEFAULT_NOT_SET = 'lang_select.default_not_set'
    LANG_SELECT_OPTIONS_PREFIX = 'lang_select.options_prefix'
    LANG_SELECT_OPTIONS_SUFFIX = 'lang_select.options_suffix'
    LANG_SELECT_PROMPT = 'lang_select.prompt'
    SETTINGS_EMPTY_CONFIG_FILE = 'settings.empty_config_file'
    SETTINGS_GIT_LABEL_NOT_FOUND = 'settings.git_label_not_found'
    SETTINGS_REMOTE_SOURCES_REGISTERED = 'settings.remote_sources_registered'
