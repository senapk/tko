from __future__ import annotations

PT_BR_TRANSLATIONS: dict[str, str] = {
    'tester.compile_error_during_run': 'CompileError durante execução do tester',
    'tester.press_enter_to_continue': 'Pressione enter para continuar',
    'tester.task_folder_not_found': 'Warning: Pasta da tarefa não encontrada',
    'tester_navigator.locked_hint': '{arrow}\nAtividade travada\nAperte {lock_key} para destravar',
    'tester_navigator.no_log_repo': 'Nenhum repositório de logs encontrado.',
    'tester_navigator.single_solver_1': 'Seu projeto só tem um arquivo de solução.',
    'tester_navigator.single_solver_2': 'Essa funcionalidade troca qual dos arquivos',
    'tester_navigator.single_solver_3': 'de solução será o principal.',
    'tester_top_bar.compile_error': 'Erro de compilação',
    'tester_top_bar.no_tests_registered': 'Nenhum teste cadastrado',
    'tester_top_bar.running_locked_activity': 'Executando atividade travada',
}

EN_TRANSLATIONS: dict[str, str] = {
    'tester.compile_error_during_run': 'CompileError during tester run',
    'tester.press_enter_to_continue': 'Press Enter to continue',
    'tester.task_folder_not_found': 'Warning: Task folder not found',
    'tester_navigator.locked_hint': '{arrow}\nLocked activity\nPress {lock_key} to unlock',
    'tester_navigator.no_log_repo': 'No log repository found.',
    'tester_navigator.single_solver_1': 'Your project has only one solution file.',
    'tester_navigator.single_solver_2': 'This feature switches which solution file',
    'tester_navigator.single_solver_3': 'will be used as the main one.',
    'tester_top_bar.compile_error': 'Compilation error',
    'tester_top_bar.no_tests_registered': 'No tests registered',
    'tester_top_bar.running_locked_activity': 'Running locked activity',
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "pt-BR": PT_BR_TRANSLATIONS,
    "en": EN_TRANSLATIONS,
}
