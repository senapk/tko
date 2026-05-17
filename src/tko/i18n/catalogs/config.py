from __future__ import annotations

PT_BR_TRANSLATIONS: dict[str, str] = {
    'config.borders_status': 'Bordas agora está: {status}',
    'config.diff_mode_down': 'Modo de diferença agora é: CIMA_BAIXO',
    'config.diff_mode_side': 'Modo de diferença agora é: LADO_A_LADO',
    'config.editor_changed': 'Novo comando para abrir arquivos de código: {editor}',
    'config.images_status': 'Imagens agora está: {status}',
    'config.lang_empty': 'Configurações de linguagem vazias',
    'config.lang_load_failed': 'Erro ao carregar as configurações de linguagem {path}, resetando para as configurações padrão',
    'config.timeout_changed': 'Novo timeout: {timeout}',
    'lang_select.default_not_set': 'Linguagem padrão ainda não foi definida.',
    'lang_select.options_prefix': '[',
    'lang_select.options_suffix': ']',
    'lang_select.prompt': 'Escolha entre as opções a seguir',
    'settings.empty_config_file': 'Arquivo de configuração vazio: {path}',
    'settings.git_label_not_found': 'Repositório git label {alias} não encontrado',
    'settings.remote_sources_registered': 'Fontes de tarefas remotas cadastradas:',
}

EN_TRANSLATIONS: dict[str, str] = {
    'config.borders_status': 'Borders now is: {status}',
    'config.diff_mode_down': 'Diff mode now is: UP_DOWN',
    'config.diff_mode_side': 'Diff mode now is: SIDE_BY_SIDE',
    'config.editor_changed': 'New command to open source files: {editor}',
    'config.images_status': 'Images now is: {status}',
    'config.lang_empty': 'Language settings are empty',
    'config.lang_load_failed': 'Error loading language settings {path}, resetting to default settings',
    'config.timeout_changed': 'New timeout: {timeout}',
    'lang_select.default_not_set': 'Default language has not been set yet.',
    'lang_select.options_prefix': '[',
    'lang_select.options_suffix': ']',
    'lang_select.prompt': 'Choose from the following options',
    'settings.empty_config_file': 'Empty config file: {path}',
    'settings.git_label_not_found': 'Git repository label {alias} not found',
    'settings.remote_sources_registered': 'Registered remote task sources:',
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "pt-BR": PT_BR_TRANSLATIONS,
    "en": EN_TRANSLATIONS,
}
