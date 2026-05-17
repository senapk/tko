from __future__ import annotations

PT_BR_TRANSLATIONS: dict[str, str] = {
    'app.context_not_set': 'Erro: O contexto da aplicação não está configurado corretamente.',
    'app.keyboard_interrupt': 'Interrupção de teclado',
    'app.version': 'tko {version}',
    'open.action_hint': '[g]Ação[.]: Navegue ou passe o caminho até a pasta do repositório e tente novamente.',
    'open.invalid_repo': '[r]Erro[.]: O comando [g]tko open[.] deve ser executado na pasta onde o repositório foi iniciado.',
    'reset.languages_path': 'Configurações de linguagem:',
    'reset.no_repo': 'Nenhum repositório TKO encontrado.',
    'reset.settings_path': 'Arquivo global configuração:',
    'ui.language_changed': 'Idioma da interface alterado para {language}',
}

EN_TRANSLATIONS: dict[str, str] = {
    'app.context_not_set': 'Error: App context is not properly set.',
    'app.keyboard_interrupt': 'Keyboard Interrupt',
    'app.version': 'tko {version}',
    'open.action_hint': '[g]Action[.]: Navigate to that folder or pass its path and try again.',
    'open.invalid_repo': '[r]Error[.]: The [g]tko open[.] command must run in the folder where the repository was initialized.',
    'reset.languages_path': 'Language settings:',
    'reset.no_repo': 'No TKO repository found.',
    'reset.settings_path': 'Global settings file:',
    'ui.language_changed': 'Interface language changed to {language}',
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "pt-BR": PT_BR_TRANSLATIONS,
    "en": EN_TRANSLATIONS,
}
