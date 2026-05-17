from __future__ import annotations

PT_BR_TRANSLATIONS: dict[str, str] = {
    'task_editor.opening_link_log': 'Opening link for task: {task_key}, URL: {url}',
    'task_editor.target_log': 'Target: {target}',
}

EN_TRANSLATIONS: dict[str, str] = {
    'task_editor.opening_link_log': 'Opening link for task: {task_key}, URL: {url}',
    'task_editor.target_log': 'Target: {target}',
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "pt-BR": PT_BR_TRANSLATIONS,
    "en": EN_TRANSLATIONS,
}
