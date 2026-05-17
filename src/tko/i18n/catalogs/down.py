from __future__ import annotations

PT_BR_TRANSLATIONS: dict[str, str] = {
    'down.activity_already_present': 'Atividade já está no repositório, precisa baixar nenhum arquivo',
    'down.activity_downloaded_success': 'Atividade baixada com sucesso',
    'down.choose_draft_extension': 'Escolha uma extensão para os rascunhos: [{options}]: ',
    'down.copy_new_drafts_manually': 'Se quiser utilizar os novos rascunhos, copie manualmente',
    'down.copy_new_drafts_to_lang': 'os novos rascunhos para a pasta {lang}',
    'down.creating_new_draft_folder': 'Criando nova pasta de rascunhos: {folder}',
    'down.file_empty': '{path} (Vazio)',
    'down.file_new': '{path} (Novo)',
    'down.file_not_overwritten': '{path} (Não sobrescrito)',
    'down.file_unchanged': '{path} (Inalterado)',
    'down.file_updated': '{path} (Atualizado)',
    'down.invalid_repo_arg': 'O parâmetro para o comando tko down deve a pasta onde você iniciou o repositório.',
    'down.invalid_repo_arg_action': 'Navegue ou passe o caminho até a pasta do repositório e tente novamente.',
    'down.latest_draft': 'Último rascunho em {name}',
    'down.link_has_no_download': 'falha: link para atividade não possui link para download',
}

EN_TRANSLATIONS: dict[str, str] = {
    'down.activity_already_present': 'Activity is already in the repository; no files need to be downloaded',
    'down.activity_downloaded_success': 'Activity downloaded successfully',
    'down.choose_draft_extension': 'Choose a draft extension: [{options}]: ',
    'down.copy_new_drafts_manually': 'If you want to use the new drafts, copy them manually',
    'down.copy_new_drafts_to_lang': 'the new drafts to folder {lang}',
    'down.creating_new_draft_folder': 'Creating new drafts folder: {folder}',
    'down.file_empty': '{path} (Empty)',
    'down.file_new': '{path} (New)',
    'down.file_not_overwritten': '{path} (Not overwritten)',
    'down.file_unchanged': '{path} (Unchanged)',
    'down.file_updated': '{path} (Updated)',
    'down.invalid_repo_arg': 'The argument for tko down must be the folder where you initialized the repository.',
    'down.invalid_repo_arg_action': 'Navigate to that folder or pass its path and try again.',
    'down.latest_draft': 'Latest draft in {name}',
    'down.link_has_no_download': 'fail: activity link does not provide a download link',
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "pt-BR": PT_BR_TRANSLATIONS,
    "en": EN_TRANSLATIONS,
}
