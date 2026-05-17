from __future__ import annotations

from enum import Enum
import os
from typing import Any


class MsgKey(str, Enum):
    APP_VERSION = "app.version"
    APP_CONTEXT_NOT_SET = "app.context_not_set"
    APP_KEYBOARD_INTERRUPT = "app.keyboard_interrupt"
    REPO_STARTER_LANGUAGE_SET = "repo_starter.language_set"
    REPO_STARTER_OPEN_HINT = "repo_starter.open_hint"
    REPO_STARTER_EXISTS = "repo_starter.exists"
    REPO_STARTER_RESET_PROMPT = "repo_starter.reset_prompt"
    REPO_STARTER_INSIDE_OTHER_REPO = "repo_starter.inside_other_repo"
    REPO_STARTER_OVERWRITE_PROMPT = "repo_starter.overwrite_prompt"
    REPO_STARTER_DEEP_REPO_WARN = "repo_starter.deep_repo_warn"
    REPO_STARTER_DEEP_REPO_WARN_2 = "repo_starter.deep_repo_warn_2"
    REPO_STARTER_EMPTY_REPO = "repo_starter.empty_repo"
    RESET_NO_REPO = "reset.no_repo"
    RESET_SETTINGS_PATH = "reset.settings_path"
    RESET_LANGUAGES_PATH = "reset.languages_path"
    OPEN_INVALID_REPO = "open.invalid_repo"
    OPEN_ACTION_HINT = "open.action_hint"
    DOWN_INVALID_REPO_ARG = "down.invalid_repo_arg"
    DOWN_INVALID_REPO_ARG_ACTION = "down.invalid_repo_arg_action"
    DOWN_ACTIVITY_ALREADY_PRESENT = "down.activity_already_present"
    DOWN_LINK_HAS_NO_DOWNLOAD = "down.link_has_no_download"
    DOWN_CREATING_NEW_DRAFT_FOLDER = "down.creating_new_draft_folder"
    DOWN_COPY_NEW_DRAFTS_MANUALLY = "down.copy_new_drafts_manually"
    DOWN_COPY_NEW_DRAFTS_TO_LANG = "down.copy_new_drafts_to_lang"
    DOWN_LATEST_DRAFT = "down.latest_draft"
    DOWN_ACTIVITY_DOWNLOADED_SUCCESS = "down.activity_downloaded_success"
    DOWN_CHOOSE_DRAFT_EXTENSION = "down.choose_draft_extension"
    DOWN_FILE_NEW = "down.file_new"
    DOWN_FILE_UPDATED = "down.file_updated"
    DOWN_FILE_UNCHANGED = "down.file_unchanged"
    DOWN_FILE_EMPTY = "down.file_empty"
    DOWN_FILE_NOT_OVERWRITTEN = "down.file_not_overwritten"
    GRADE_HEADER = "grade.header"
    GRADE_FOOTER = "grade.footer"
    GRADE_AUTO_MODE_LABEL = "grade.auto_mode_label"
    GRADE_MANUAL_MODE_LABEL = "grade.manual_mode_label"
    GRADE_STUDY_TIME_LABEL = "grade.study_time_label"
    GRADE_FRIEND_LABEL = "grade.friend_label"
    GRADE_GUIDED_LABEL = "grade.guided_label"
    GRADE_GUIDED_DISCOUNT = "grade.guided_discount"
    GRADE_CONCEPT_LABEL = "grade.concept_label"
    GRADE_CONCEPT_DISCOUNT = "grade.concept_discount"
    GRADE_PROBLEM_LABEL = "grade.problem_label"
    GRADE_PROBLEM_DISCOUNT = "grade.problem_discount"
    GRADE_CODE_LABEL = "grade.code_label"
    GRADE_CODE_DISCOUNT = "grade.code_discount"
    GRADE_DEBUG_LABEL = "grade.debug_label"
    GRADE_DEBUG_DISCOUNT = "grade.debug_discount"
    GRADE_REFACTOR_LABEL = "grade.refactor_label"
    GRADE_REFACTOR_DISCOUNT = "grade.refactor_discount"
    GRADE_SECTION_TITLE = "grade.section_title"
    GRADE_SECTION_HUMAN_HELP = "grade.section_human_help"
    GRADE_SECTION_AI_USAGE = "grade.section_ai_usage"
    GRADE_YES = "grade.yes"
    GRADE_NO = "grade.no"
    GRADE_NOTHING = "grade.nothing"
    GUI_LEFT_PANEL_SEARCH = "gui_left_panel.search"
    GUI_LEFT_PANEL_OUTDATED = "gui_left_panel.outdated"
    GUI_LEFT_PANEL_UPDATE_MESSAGE = "gui_left_panel.update_message"
    GUI_LEFT_PANEL_UPDATE_COMMAND = "gui_left_panel.update_command"
    CALIBRATE_LEFT = "calibrate.left"
    CALIBRATE_RIGHT = "calibrate.right"
    CALIBRATE_UP = "calibrate.up"
    CALIBRATE_DOWN = "calibrate.down"
    CALIBRATE_ESC = "calibrate.esc"
    CALIBRATE_PAGE_UP = "calibrate.page_up"
    CALIBRATE_PAGE_DOWN = "calibrate.page_down"
    CALIBRATE_BACKSPACE = "calibrate.backspace"
    INPUT_TEXT_PROMPT = "input_text.prompt"
    RUN_TESTING_LABEL = "run.testing_label"
    RUN_NO_SOURCE_FILES = "run.no_source_files"
    RUN_NO_SOURCE_OR_TESTS = "run.no_source_or_tests"
    RUN_NO_TEST_CASES = "run.no_test_cases"
    RUN_NO_CODE_FOUND = "run.no_code_found"
    RUN_PACK_LOAD_FAILED = "run.pack_load_failed"
    RUN_AUTOLOAD_FOLDER_NOT_SET = "run.autoload_folder_not_set"
    RUN_AUTOLOAD_LANG_HINT = "run.autoload_lang_hint"
    RUN_FILTER_INDEX_OUT_OF_BOUNDS = "run.filter_index_out_of_bounds"
    RUN_TASK_NOT_DEFINED = "run.task_not_defined"
    RUN_TARGET_NOT_FOUND = "run.target_not_found"
    SOLVER_COMMAND_NOT_FOUND = "solver.command_not_found"
    SOLVER_EXTENSION_UNRECOGNIZED = "solver.extension_unrecognized"
    SOLVER_TS_CONFIG_NOT_FOUND = "solver.ts_config_not_found"
    CONFIG_BORDERS_STATUS = "config.borders_status"
    CONFIG_IMAGES_STATUS = "config.images_status"
    CONFIG_DIFF_MODE_SIDE = "config.diff_mode_side"
    CONFIG_DIFF_MODE_DOWN = "config.diff_mode_down"
    CONFIG_EDITOR_CHANGED = "config.editor_changed"
    CONFIG_TIMEOUT_CHANGED = "config.timeout_changed"
    CONFIG_LANG_EMPTY = "config.lang_empty"
    CONFIG_LANG_LOAD_FAILED = "config.lang_load_failed"
    SETTINGS_GIT_LABEL_NOT_FOUND = "settings.git_label_not_found"
    SETTINGS_EMPTY_CONFIG_FILE = "settings.empty_config_file"
    SETTINGS_REMOTE_SOURCES_REGISTERED = "settings.remote_sources_registered"
    GAME_BUILDER_README_FETCH_ERROR = "game_builder.readme_fetch_error"
    GAME_BUILDER_SOURCE_NOT_FOUND = "game_builder.source_not_found"
    GAME_BUILDER_SOURCE_NOT_FOUND_CREATING = "game_builder.source_not_found_creating"
    GAME_BUILDER_SOURCE_NO_ORIGIN_DIR = "game_builder.source_no_origin_dir"
    GAME_BUILDER_INDEX_FETCH_ERROR = "game_builder.index_fetch_error"
    GAME_BUILDER_QUEST_REQUIRES_MISSING = "game_builder.quest_requires_missing"
    GAME_BUILDER_NO_QUEST_TITLE = "game_builder.no_quest_title"
    GAME_TASK_NOT_FOUND_IN_COURSE = "game.task_not_found_in_course"
    GAME_BUILD_FAILED_FOR_SOURCE = "game.build_failed_for_source"
    LOADER_TARGET_FORMAT_NOT_SUPPORTED = "loader.target_format_not_supported"
    LOADER_UNABLE_TO_FIND = "loader.unable_to_find"
    TOML_CASE_INVALID = "toml.case_invalid"
    TOML_CASE_DATA_WARNING = "toml.case_data_warning"
    MDPP_MISSING_EXTRACT_VALUE = "mdpp.missing_extract_value"
    MDPP_INVALID_TESTS_INTEGER = "mdpp.invalid_tests_integer"
    MDPP_UNRECOGNIZED_TAG = "mdpp.unrecognized_tag"
    MDPP_FILE_NOT_FOUND = "mdpp.file_not_found"
    MDPP_FILE_UPDATED = "mdpp.file_updated"
    MDPP_FILE_NOT_MARKDOWN = "mdpp.file_not_markdown"
    FENO_HTML_MARKDOWN_NOT_FOUND = "feno_html.markdown_not_found"
    FENO_HTML_CONVERSION_ERROR = "feno_html.conversion_error"
    FENO_BUILD_NO_TARGET_SPECIFIED = "feno_build.no_target_specified"
    FENO_BUILD_TARGET_NOT_DIRECTORY = "feno_build.target_not_directory"
    FENO_GITHUB_CFG_NOT_SET = "feno_github_cfg.not_set"
    GAME_SANDBOX_SOURCE_NOT_FOUND = "game.sandbox_source_not_found"
    RUN_FILTER_MODE_BANNER = "run.filter_mode_banner"
    REPOSITORY_DATA_LOAD_ERROR = "repository_data.load_error"
    REMOTE_GIT_CACHE_ROOT_REQUIRED = "remote.git_cache_root_required"
    REMOTE_SANDBOX_ONLY_TRUE = "remote.sandbox_only_true"
    REMOTE_PATH_SOURCE_DIR_NOT_EXISTS = "remote_path.source_dir_not_exists"
    REMOTE_PATH_INDEX_FILE_NOT_EXISTS = "remote_path.index_file_not_exists"
    GAME_COORDINATOR_LOADING_REPOSITORY = "game_coordinator.loading_repository"
    TASK_PARSER_VIEW_EXTERNAL_URL = "task_parser.view_external_url"
    TASK_PARSER_EDIT_EXTERNAL_URL = "task_parser.edit_external_url"
    PATTERN_WILDCARD_ONLY_ONCE = "pattern.wildcard_only_once"
    PATTERN_INPUT_WILDCARD_REQUIRES_OUTPUT = "pattern.input_wildcard_requires_output"
    PATTERN_OUTPUT_WILDCARD_REQUIRES_INPUT = "pattern.output_wildcard_requires_input"
    PATTERN_OUTPUT_FILE_NOT_FOUND = "pattern.output_file_not_found"
    INDEXER_INVALID_LABEL = "indexer.invalid_label"
    INDEXER_FOUND_READMES = "indexer.found_readmes"
    INDEXER_MISSING_README_REMOVING = "indexer.missing_readme_removing"
    INDEXER_MISSING_README_TASK = "indexer.missing_readme_task"
    INDEXER_MISMATCH_TITLE = "indexer.mismatch_title"
    INDEXER_REPLACE_TITLE_README_MISSING = "indexer.replace_title_readme_missing"
    INDEXER_REPLACED_TITLE = "indexer.replaced_title"
    INDEXER_MISSING_HOOKS_ADDING = "indexer.missing_hooks_adding"
    COLLECTED_NO_RESUME_DATA = "collected.no_resume_data"
    FLOATING_INVALID_ALIGN = "floating.invalid_align"
    TASK_EDITOR_OPENING_LINK_LOG = "task_editor.opening_link_log"
    TASK_EDITOR_TARGET_LOG = "task_editor.target_log"
    CLI_REMOTE_ADD_SOURCE_ERROR = "cli.remote_add_source_error"
    LABEL_FACTORY_INDEX_INT_REQUIRED = "label_factory.index_int_required"
    GITHUB_URL_INVALID_URL = "github_url.invalid_url"
    GITHUB_URL_INVALID_GITHUB_URL = "github_url.invalid_github_url"
    EXECUTION_RESULT_INVALID_TYPE = "execution_result.invalid_type"
    FILTER_FILE_NOT_FOUND = "filter.file_not_found"
    FILTER_TARGET_MUST_BE_FOLDER = "filter.target_must_be_folder"
    FILTER_OUTPUT_FOLDER_REQUIRED = "filter.output_folder_required"
    FILTER_OUTPUT_FOLDER_EXISTS = "filter.output_folder_exists"
    FILTER_ACTION_PATH = "filter.action_path"
    FILTER_ACTION_DISABLED_PATH = "filter.action_disabled_path"
    GIT_CACHE_CLEARING = "git_cache.clearing"
    GIT_CACHE_CLONING = "git_cache.cloning"
    GIT_CACHE_CLONE_FAILED = "git_cache.clone_failed"
    GIT_CACHE_UPDATING = "git_cache.updating"
    GIT_CACHE_UPDATE_FAILED_RECLONE = "git_cache.update_failed_reclone"
    GRADING_README_NOT_FOUND = "grading.readme_not_found"
    GRADING_NO_PROBLEMS_FOUND = "grading.no_problems_found"
    GRADING_RUNNING_PREFIX = "grading.running_prefix"
    GRADING_GRADING_PREFIX = "grading.grading_prefix"
    TRACKER_NOT_ENOUGH_COLUMNS = "tracker.not_enough_columns"
    TRACKER_INVALID_TIMESTAMP_FORMAT = "tracker.invalid_timestamp_format"
    LOGGER_INVALID_ITEM_TYPE = "logger.invalid_item_type"
    LOGGER_LOG_FOLDER_NOT_DIR = "logger.log_folder_not_dir"
    LOGGER_UNKNOWN_ACTION = "logger.unknown_action"
    FMT_NOT_INITIALIZED = "fmt.not_initialized"
    INPUT_DUPLICATE_KEY = "input.duplicate_key"
    TASK_LAUNCHER_FOLDER_NOT_FOUND = "task_launcher.folder_not_found"
    TASK_LAUNCHER_NO_SOURCE_FOR_LANG = "task_launcher.no_source_for_lang"
    TASK_LAUNCHER_DRAFT_CREATED = "task_launcher.draft_created"
    PLAY_KEY_NOT_RECOGNIZED = "play.key_not_recognized"
    DRAFT_CREATOR_TITLE_PROMPT = "draft_creator.title_prompt"
    DRAFT_CREATOR_TITLE_PLACEHOLDER = "draft_creator.title_placeholder"
    DRAFT_CREATOR_FOLDER_EXISTS = "draft_creator.folder_exists"
    DRAFT_CREATOR_CREATED_AT = "draft_creator.created_at"
    PLAY_ACTION_TASK_NO_LOCAL_FOLDER = "play_action.task_no_local_folder"
    PLAY_ACTION_ONLY_TASK_FOLDERS = "play_action.only_task_folders"
    PLAY_ACTION_DELETE_CONFIRM_PREFIX = "play_action.delete_confirm_prefix"
    GAME_VALIDATOR_DUPLICATE_KEY = "game_validator.duplicate_key"
    GAME_VALIDATOR_SELF_REF_ERROR = "game_validator.self_ref_error"
    GAME_VALIDATOR_CYCLE_DETECTED = "game_validator.cycle_detected"
    TASK_PATH_VIEW_NO_WORKDIR = "task_path.view_no_workdir"
    TASK_PATH_INVALID_LOCAL_PATH = "task_path.invalid_local_path"
    FREERUN_PROMPT_RERUN = "freerun.prompt_rerun"
    FREERUN_PROMPT_BACK = "freerun.prompt_back"
    TEXT_MUST_BE_STRING = "text.must_be_string"
    TEXT_INDEX_OUT_OF_RANGE = "text.index_out_of_range"
    REPOSITORY_LOADER_GIT_CONFLICT = "repository_loader.git_conflict"
    REPOSITORY_LOADER_EMPTY_CONFIG_FILE = "repository_loader.empty_config_file"
    REPOSITORY_LOADER_YAML_CORRUPTED = "repository_loader.yaml_corrupted"
    REPOSITORY_LOADER_CONFIG_EMPTY = "repository_loader.config_empty"
    REPOSITORY_LOADER_CONFIG_CORRUPTED_UNEXPECTED = "repository_loader.config_corrupted_unexpected"
    LANG_SELECT_DEFAULT_NOT_SET = "lang_select.default_not_set"
    LANG_SELECT_PROMPT = "lang_select.prompt"
    LANG_SELECT_OPTIONS_PREFIX = "lang_select.options_prefix"
    LANG_SELECT_OPTIONS_SUFFIX = "lang_select.options_suffix"
    REMOTE_EDIT_HINT = "remote.edit_hint"
    REMOTE_NONE_CONFIGURED = "remote.none_configured"
    REMOTE_CONFIGURED_SOURCES = "remote.configured_sources"
    REMOTE_LABEL = "remote.label"
    REMOTE_LINK = "remote.link"
    REMOTE_INDEX = "remote.index"
    REMOTE_QUEST_FILTER = "remote.quest_filter"
    REMOTE_FILTER_DISABLED = "remote.filter_disabled"
    REMOTE_FILTER_ENABLED = "remote.filter_enabled"
    REMOTE_REMOVED_SUCCESS = "remote.removed_success"
    REMOTE_NOT_FOUND = "remote.not_found"
    REMOTE_FILTERS_UPDATED = "remote.filters_updated"
    REMOTE_NAME_EXISTS = "remote.name_exists"
    REMOTE_ADDING_GIT = "remote.adding_git"
    REMOTE_GIT_ALIAS_NOT_FOUND = "remote.git_alias_not_found"
    REMOTE_CLONE_ERROR = "remote.clone_error"
    REMOTE_CLONE_FAILED = "remote.clone_failed"
    REMOTE_DIR_NOT_FOUND = "remote.dir_not_found"
    REMOTE_ADDING_LOCAL = "remote.adding_local"
    REMOTE_ADDING_URL = "remote.adding_url"
    REMOTE_ADDED_SUCCESS = "remote.added_success"
    REMOTE_CLONING = "remote.cloning"
    REMOTE_CLONED_SUCCESS = "remote.cloned_success"
    REMOTE_CAN_ACCESS = "remote.can_access"
    PULL_UNEXPECTED_ERROR = "pull.unexpected_error"
    PULL_UP_TO_DATE = "pull.up_to_date"
    PULL_FETCH_LABEL = "pull.fetch_label"
    PULL_FETCH_FAILED = "pull.fetch_failed"
    PULL_UPDATE_LABEL = "pull.update_label"
    PULL_FALLBACK_LABEL = "pull.fallback_label"
    PULL_RESET_FAILED = "pull.reset_failed"
    PULL_ALL_PARALLEL = "pull.all_parallel"
    PULL_ERROR_IN_REPO = "pull.error_in_repo"
    PULL_COMPLETED = "pull.completed"
    CLI_COMMON_GLOBAL_CACHE = "cli.common.global_cache"
    CLI_COMMON_NO_REPO = "cli.common.no_repo"
    CLI_TOOL_MDPP_UPDATING_README = "cli.tool.mdpp_updating_readme"
    CLI_TOOL_REBASE_URL_DOWNLOADED = "cli.tool.rebase_url_downloaded"
    CLI_TOOL_REBASE_DONE = "cli.tool.rebase_done"
    CLI_TOOL_REBASE_SAVED_PATH = "cli.tool.rebase_saved_path"
    CLI_TOOL_REBASE_ALIAS_README_FAILED = "cli.tool.rebase_alias_readme_failed"
    CLI_TOOL_HTML_INPUT_MD_REQUIRED = "cli.tool.html_input_md_required"
    CLI_TOOL_HTML_OUTPUT_HTML_REQUIRED = "cli.tool.html_output_html_required"
    CMD_BUILD_EXECUTE_FAILED = "cmd.build_execute_failed"
    CMD_COLLECT_REPO_NOT_FOUND = "cmd.collect_repo_not_found"
    CMD_COLLECT_TKO_REPO_NOT_FOUND = "cmd.collect_tko_repo_not_found"
    CMD_COLLECT_MULTIPLE_REPOS_FOUND = "cmd.collect_multiple_repos_found"
    CMD_COLLECT_RUNNING_IN = "cmd.collect_running_in"
    CMD_COLLECT_JSON_PARSE_FAILED = "cmd.collect_json_parse_failed"
    CMD_COLLECT_ERROR = "cmd.collect_error"
    CMD_COLLECT_SAVING_EXTRACTED_DATA = "cmd.collect_saving_extracted_data"
    CMD_DOWN_ACTIVITY_LINK_NOT_DOWNLOADABLE = "cmd.down_activity_link_not_downloadable"
    CMD_DOWN_ACTIVITY_NO_ORIGIN_FOLDER = "cmd.down_activity_no_origin_folder"
    CMD_DOWN_ACTIVITY_NO_DESTINY_FOLDER = "cmd.down_activity_no_destiny_folder"
    CLI_CONFIG_SETTINGS_FILE = "cli.config_settings_file"
    CLI_REMOTE_CLEAR_WITH_QUEST_ERROR = "cli.remote_clear_with_quest_error"
    CLI_BUILD_UPDATING_DRAFTS = "cli.build_updating_drafts"
    WRITER_NO_CHANGES_TEST_FILE = "writer.no_changes_test_file"
    WRITER_FILE_WROTE = "writer.file_wrote"
    WRITER_TARGET_NOT_SUPPORTED_BUILD = "writer.target_not_supported_build"
    TASK_CODE_NOT_FOUND = "task.code_not_found"
    TASK_CODE_ONLY_DOWNLOADED = "task.code_only_downloaded"
    TASK_OPENING_LINK = "task.opening_link"
    TASK_IS_MISSION = "task.is_mission"
    TASK_LINK_ONLY_TASKS = "task.link_only_tasks"
    TASK_VERSIONS_DECOMPRESSED = "task.versions_decompressed"
    TASK_VERSIONS_OPENING = "task.versions_opening"
    LOADER_FAILED_TO_LOAD = "loader.failed_to_load"
    GUI_TOP_BAR_RECOMMENDED = "gui_top_bar.recommended"
    GUI_TOP_BAR_ALL = "gui_top_bar.all"
    GUI_TOP_BAR_GRAPHS = "gui_top_bar.graphs"
    GUI_TOP_BAR_LOGS = "gui_top_bar.logs"
    GUI_TOP_BAR_SKILLS = "gui_top_bar.skills"
    GUI_TOP_BAR_HELP = "gui_top_bar.help"
    GUI_TOP_BAR_EXEC = "gui_top_bar.exec"
    GUI_TOP_BAR_TIME = "gui_top_bar.time"
    TESTER_TASK_FOLDER_NOT_FOUND = "tester.task_folder_not_found"
    TESTER_TOP_BAR_RUNNING_LOCKED_ACTIVITY = "tester_top_bar.running_locked_activity"
    TESTER_TOP_BAR_NO_TESTS_REGISTERED = "tester_top_bar.no_tests_registered"
    TESTER_TOP_BAR_COMPILE_ERROR = "tester_top_bar.compile_error"
    TESTER_NAVIGATOR_LOCKED_HINT = "tester_navigator.locked_hint"
    TESTER_NAVIGATOR_SINGLE_SOLVER_1 = "tester_navigator.single_solver_1"
    TESTER_NAVIGATOR_SINGLE_SOLVER_2 = "tester_navigator.single_solver_2"
    TESTER_NAVIGATOR_SINGLE_SOLVER_3 = "tester_navigator.single_solver_3"
    TESTER_NAVIGATOR_NO_LOG_REPO = "tester_navigator.no_log_repo"
    TESTER_COMPILE_ERROR_DURING_RUN = "tester.compile_error_during_run"
    TESTER_PRESS_ENTER_TO_CONTINUE = "tester.press_enter_to_continue"
    TASK_DOWNLOAD_IS_MISSION = "task.download_is_mission"
    TASK_DOWNLOAD_ONLY_TASKS = "task.download_only_tasks"
    TASK_DOWNLOAD_NOT_IMPORTABLE = "task.download_not_importable"
    TASK_DOWNLOAD_HEADER = "task.download_header"
    TASK_DELETE_NOT_MATCH = "task.delete_not_match"
    TASK_DELETE_SUCCESS = "task.delete_success"
    PLAY_ACTION_DELETE_ERROR = "play.action.delete_error"
    PLAY_PALETTE_DOWN_TASK = "play.palette.down_task"
    PLAY_PALETTE_EVALUATE = "play.palette.evaluate"
    PLAY_PALETTE_DELETE = "play.palette.delete"
    PLAY_PALETTE_HELP = "play.palette.help"
    PLAY_PALETTE_BORDERS = "play.palette.borders"
    PLAY_PALETTE_IMAGES = "play.palette.images"
    PLAY_PALETTE_TIME = "play.palette.time"
    PLAY_PALETTE_LANGUAGE = "play.palette.language"
    PLAY_PALETTE_CALIBRATE = "play.palette.calibrate"
    PLAY_PALETTE_DRAFT = "play.palette.draft"
    PLAY_PALETTE_RELOAD = "play.palette.reload"
    PLAY_PALETTE_VERSIONS = "play.palette.versions"
    PLAY_PALETTE_PANEL_SIZE = "play.palette.panel_size"


_SUPPORTED_LANGUAGES = {"pt-BR", "en"}
_LANGUAGE_ALIASES = {
    "pt": "pt-BR",
    "pt-br": "pt-BR",
    "pt_br": "pt-BR",
    "english": "en",
    "en-us": "en",
    "en_uk": "en",
}

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "pt-BR": {
        "app.version": "tko {version}",
        "app.context_not_set": "Erro: O contexto da aplicação não está configurado corretamente.",
        "app.keyboard_interrupt": "Interrupção de teclado",
        "repo_starter.language_set": "A linguagem do repositório foi definida como [y]{language}[.].",
        "repo_starter.open_hint": "Voce pode acessar o repositório com o comando [g]tko open[.]",
        "repo_starter.exists": "Já existe um repositório TKO na pasta [y]{folder}[.]",
        "repo_starter.reset_prompt": "Deseja resetar o repositório? ([g]s[.]/[r]n[.]): ",
        "repo_starter.inside_other_repo": "Você está tentando criar um repositório dentro de outro, pois já existe rep em [r]{parent}[.]",
        "repo_starter.overwrite_prompt": "Deseja sobrescrever as configurações do repositório em [y]{folder}[.] ? ([g]s[.]/[r]n[.]): ",
        "repo_starter.deep_repo_warn": "Você está tentando criar um repositório TKO na pasta [y]{folder}[.]",
        "repo_starter.deep_repo_warn_2": "Porém já existem repositórios TKO abaixo dessa pasta. Mova ou apague-os",
        "repo_starter.empty_repo": "Criando repositório vazio, como pasta para atividades locais",
        "reset.no_repo": "Nenhum repositório TKO encontrado.",
        "reset.settings_path": "Arquivo global configuração:",
        "reset.languages_path": "Configurações de linguagem:",
        "open.invalid_repo": "[r]Erro[.]: O comando [g]tko open[.] deve ser executado na pasta onde o repositório foi iniciado.",
        "open.action_hint": "[g]Ação[.]: Navegue ou passe o caminho até a pasta do repositório e tente novamente.",
        "down.invalid_repo_arg": "O parâmetro para o comando tko down deve a pasta onde você iniciou o repositório.",
        "down.invalid_repo_arg_action": "Navegue ou passe o caminho até a pasta do repositório e tente novamente.",
        "down.activity_already_present": "Atividade já está no repositório, precisa baixar nenhum arquivo",
        "down.link_has_no_download": "falha: link para atividade não possui link para download",
        "down.creating_new_draft_folder": "Criando nova pasta de rascunhos: {folder}",
        "down.copy_new_drafts_manually": "Se quiser utilizar os novos rascunhos, copie manualmente",
        "down.copy_new_drafts_to_lang": "os novos rascunhos para a pasta {lang}",
        "down.latest_draft": "Último rascunho em {name}",
        "down.activity_downloaded_success": "Atividade baixada com sucesso",
        "down.choose_draft_extension": "Escolha uma extensão para os rascunhos: [{options}]: ",
        "down.file_new": "{path} (Novo)",
        "down.file_updated": "{path} (Atualizado)",
        "down.file_unchanged": "{path} (Inalterado)",
        "down.file_empty": "{path} (Vazio)",
        "down.file_not_overwritten": "{path} (Não sobrescrito)",
        "grade.header": " Utilize os direcionais e texto para marcar",
        "grade.footer": " Pressione Enter para confirmar, Esc para cancelar",
        "grade.auto_mode_label": "Taxa de testes que passou na última execução:",
        "grade.manual_mode_label": "Informe qual percentual da atividade você fez?",
        "grade.study_time_label": "Qual tempo total estimado, estudo + código, em minutos?",
        "grade.friend_label": "Deixe em branco se fez sozinho, ou com o nome de quem ajudou",
        "grade.guided_label": "Fez o código copiando da aula ou vídeo aula?",
        "grade.guided_discount": "COPIOU:",
        "grade.concept_label": "ESTUDAR conceitos sem gerar a solução do problema?",
        "grade.concept_discount": "ESTUDAR:",
        "grade.problem_label": "ENTENDER o problema a ser resolvido?",
        "grade.problem_discount": "ENTENDER:",
        "grade.code_label": "GERAR ou CORRIGIR código relacionado ao problema?",
        "grade.code_discount": "CORRIGIR:",
        "grade.debug_label": "COMPREENDER mensagens de ERRO ou SAÍDA incorreta?",
        "grade.debug_discount": "DEBUGAR:",
        "grade.refactor_label": "REFATORAR o código só após fazer tudo sozinho?",
        "grade.refactor_discount": "REFATORAR:",
        "grade.section_title": "Pontue de acordo com a última vez que você (re)fez a tarefa do zero (sprint)",
        "grade.section_human_help": "Você fez com ajuda humana ou guiado?",
        "grade.section_ai_usage": "Você usou IA (LLMs) para",
        "grade.yes": "Sim",
        "grade.no": "Não",
        "grade.nothing": " Nada",
        "gui_left_panel.search": " Busca: ",
        "gui_left_panel.outdated": " TKO DESATUALIZADO!",
        "gui_left_panel.update_message": " Atualize com: ",
        "gui_left_panel.update_command": "pipx upgrade tko ",
        "calibrate.left": "Esquerda",
        "calibrate.right": "Direita",
        "calibrate.up": "Cima",
        "calibrate.down": "Baixo",
        "calibrate.esc": "Esc",
        "calibrate.page_up": "PgUp",
        "calibrate.page_down": "PgDn",
        "calibrate.backspace": "Backspace",
        "input_text.prompt": "Digite aqui: ",
        "run.testing_label": " Testando o código com os casos de teste ",
        "run.no_source_files": "Nenhum arquivo de código encontrado.",
        "run.no_source_or_tests": "Nenhum arquivo de código ou de teste encontrado.",
        "run.no_test_cases": "Nenhum caso de teste encontrado.",
        "run.no_code_found": "Nenhum arquivo de código encontrado. Listando casos de teste.",
        "run.pack_load_failed": "Falha ao carregar pacote de unidades em {source}",
        "run.autoload_folder_not_set": "fail: pasta de autoload não definida",
        "run.autoload_lang_hint": "Você não definiu os arquivos diretamente. Use [y]-l[.] caso queira especificar a linguagem para autoloading.",
        "run.filter_index_out_of_bounds": "Índice fora dos limites: {index}",
        "run.task_not_defined": "Task não definida",
        "run.target_not_found": "fail: {target} não encontrado",
        "solver.command_not_found": "fail: comando '{name}' não foi encontrado",
        "solver.extension_unrecognized": "Falha: Extensão de arquivo '{suffix}' não reconhecida e sem configuração de linguagem",
        "solver.ts_config_not_found": "Falha: Configuração da linguagem 'ts' não encontrada",
        "config.borders_status": "Bordas agora está: {status}",
        "config.images_status": "Imagens agora está: {status}",
        "config.diff_mode_side": "Modo de diferença agora é: LADO_A_LADO",
        "config.diff_mode_down": "Modo de diferença agora é: CIMA_BAIXO",
        "config.editor_changed": "Novo comando para abrir arquivos de código: {editor}",
        "config.timeout_changed": "Novo timeout: {timeout}",
        "config.lang_empty": "Configurações de linguagem vazias",
        "config.lang_load_failed": "Erro ao carregar as configurações de linguagem {path}, resetando para as configurações padrão",
        "settings.git_label_not_found": "Repositório git label {alias} não encontrado",
        "settings.empty_config_file": "Arquivo de configuração vazio: {path}",
        "settings.remote_sources_registered": "Fontes de tarefas remotas cadastradas:",
        "game_builder.readme_fetch_error": "Erro ao obter o arquivo README da fonte {name}",
        "game_builder.source_not_found": "Aviso: fonte {filename} não encontrada no source {name}",
        "game_builder.source_not_found_creating": "Aviso: fonte {filename} não encontrada no source {name}, criando arquivo",
        "game_builder.source_no_origin_dir": "Aviso: fonte {name} não possui diretório de origem",
        "game_builder.index_fetch_error": "Erro ao obter o arquivo de índice da fonte {name}",
        "game_builder.quest_requires_missing": "Quest\\n{filename}:{line}\\n{quest}\\nrequer {required} que não existe",
        "game_builder.no_quest_title": "Sem Quest",
        "game.task_not_found_in_course": "fail: tarefa '{task_key}' não encontrada no curso",
        "game.build_failed_for_source": "Falha ao construir jogo para a fonte {name}",
        "loader.target_format_not_supported": "warning: formato de target não suportado: {source}",
        "loader.unable_to_find": "warning: não foi possível encontrar: {source}",
        "toml.case_invalid": "Case {index} inválido.",
        "toml.case_data_warning": "warning: dados do case {index}: {case}",
        "mdpp.missing_extract_value": "missing value for --extract",
        "mdpp.invalid_tests_integer": "invalid or missing integer for --tests",
        "mdpp.unrecognized_tag": "unrecognized tag '{tag}'",
        "mdpp.file_not_found": "file {path} not found",
        "mdpp.file_updated": "file {path} updated",
        "mdpp.file_not_markdown": "File {path} is not a markdown file",
        "feno_html.markdown_not_found": "Erro: Arquivo Markdown não encontrado em '{path}'",
        "feno_html.conversion_error": "Ocorreu um erro durante a conversão",
        "feno_build.no_target_specified": "Nenhum target especificado, usando diretório atual",
        "feno_build.target_not_directory": "fail: {target} não é um diretório",
        "feno_github_cfg.not_set": "fail: arquivo {filename} não definido",
        "game.sandbox_source_not_found": "Local sandbox source not found",
        "run.filter_mode_banner": " Entrando no modo de filtragem ",
        "repository_data.load_error": "Error loading data from dictionary",
        "remote.git_cache_root_required": "Git cache and root dir must be set to resolve the path",
        "remote.sandbox_only_true": "Sandbox source só pode ser definido como True",
        "remote_path.source_dir_not_exists": "Diretório de origem não existe",
        "remote_path.index_file_not_exists": "Arquivo de índice não existe",
        "game_coordinator.loading_repository": "Carregando repositório de {root}...",
        "task_parser.view_external_url": "Parseando tarefa de visualização com URL externa: {url}",
        "task_parser.edit_external_url": "Parseando tarefa de edição com URL externa: {url}",
        "pattern.wildcard_only_once": "  fail: o curinga @ deve ser usado apenas uma vez por padrão",
        "pattern.input_wildcard_requires_output": "  fail: se input_pattern tem o curinga @, output_pattern deve ter também",
        "pattern.output_wildcard_requires_input": "  fail: se output_pattern tem o curinga @, input_pattern deve ter também",
        "pattern.output_file_not_found": "fail: arquivo {file} não encontrado",
        "indexer.invalid_label": "Rótulo inválido na linha: {label}",
        "indexer.found_readmes": "Encontrados {count} arquivos README.md no diretório base '{base_dir}'",
        "indexer.missing_readme_removing": "Warning: README file '[y]{readme}[.]' does not exist for task:[b]{task}[.], removing from index",
        "indexer.missing_readme_task": "Warning: README file '[y]{readme}[.]' does not exist for task:[b]{task}[.]",
        "indexer.mismatch_title": "Mismatch title for task:[b]{readme}[.]\n\tREADME:'[y]{line_title}[.]' != TASK:'[g]{folder_title}[.]'",
        "indexer.replace_title_readme_missing": "Error: README file '{readme}' does not exist, cannot replace title.",
        "indexer.replaced_title": "Replaced title in '{readme}' with '{title}'",
        "indexer.missing_hooks_adding": "Found {count} missing hooks, adding to quest '{quest}':",
        "collected.no_resume_data": "No resume data found in the JSON.",
        "floating.invalid_align": "Invalid align {align}",
        "task_editor.opening_link_log": "Opening link for task: {task_key}, URL: {url}",
        "task_editor.target_log": "Target: {target}",
        "cli.remote_add_source_error": "Erro ao adicionar fonte",
        "label_factory.index_int_required": "Index on label must be a integer",
        "github_url.invalid_url": "Invalid URL",
        "github_url.invalid_github_url": "Invalid GitHub URL",
        "execution_result.invalid_type": "Invalid result type",
        "filter.file_not_found": "Aviso: Arquivo {path} não encontrado",
        "filter.target_must_be_folder": "Erro: target deve ser uma pasta no modo recursivo",
        "filter.output_folder_required": "Erro: pasta de saída deve ser especificada no modo recursivo",
        "filter.output_folder_exists": "Erro: pasta de saída já existe",
        "filter.action_path": "action: {action}, path: {path}",
        "filter.action_disabled_path": "action: disabled, path: {path}",
        "git_cache.clearing": "Limpando cache git em {cache_dir}...",
        "git_cache.cloning": "Clonando {url} para o cache...",
        "git_cache.clone_failed": "Falha ao clonar {url}. Removendo diretório de cache...",
        "git_cache.updating": "Atualizando cache para {url}...",
        "git_cache.update_failed_reclone": "Falha ao atualizar cache para {url}. Removendo e clonando novamente...",
        "grading.readme_not_found": "Arquivo README '{file}' não existe.",
        "grading.no_problems_found": "Nenhum problema encontrado no arquivo de configuração.",
        "grading.running_prefix": "[TKO RUNNING] ",
        "grading.grading_prefix": "[TKO GRADING] ",
        "tracker.not_enough_columns": "Colunas insuficientes para criar um objeto Track.",
        "tracker.invalid_timestamp_format": "Formato de timestamp inválido: {timestamp}. O formato esperado é YYYY-MM-DD_HH-MM-SS.",
        "logger.invalid_item_type": "Tipo de item inválido",
        "logger.log_folder_not_dir": "A pasta de log '{log_folder}' não é um diretório.",
        "logger.unknown_action": "Ação desconhecida {action}",
        "fmt.not_initialized": "Fmt.__scr não foi inicializado",
        "input.duplicate_key": "Chave duplicada {input_key}",
        "task_launcher.folder_not_found": "Pasta não encontrada",
        "task_launcher.no_source_for_lang": "Nenhum arquivo de código na linguagem {lang} encontrado.",
        "task_launcher.draft_created": "Um arquivo de rascunho foi criado",
        "play.key_not_recognized": "Tecla char:{char}, code:{code}, não reconhecida",
        "draft_creator.title_prompt": "Digite o Título (use @label para definir a chave manualmente)",
        "draft_creator.title_placeholder": "Digite o título da tarefa aqui",
        "draft_creator.folder_exists": "A pasta {folder} já existe.",
        "draft_creator.created_at": "Rascunho criado em {folder}",
        "play_action.task_no_local_folder": "Essa tarefa não possui pasta de código local.",
        "play_action.only_task_folders": "Você só pode apagar pastas de tarefas.",
        "play_action.delete_confirm_prefix": "Para apagar essa pasta, digite ",
        "game_validator.duplicate_key": "Chave repetida: {task_key}",
        "game_validator.self_ref_error": "Erro: auto referência {line_number} {line}",
        "game_validator.cycle_detected": "Cycle detected: {visited}",
        "task_path.view_no_workdir": "Task {task_key} is a view resource, it does not have a work directory",
        "task_path.invalid_local_path": "Task {task_key} does not have a valid local path",
        "freerun.prompt_rerun": "Para recompilar e reexecutar pressione enter",
        "freerun.prompt_back": "Para voltar para tela anterior digite q e pressione enter",
        "text.must_be_string": "text must be a string",
        "text.index_out_of_range": "index out of range",
        "repository_loader.git_conflict": "Conflito de merge git detectado em {file}.\\nResolva o conflito manualmente antes de continuar.",
        "repository_loader.empty_config_file": "Arquivo de configuração vazio: {file}",
        "repository_loader.yaml_corrupted": "O arquivo de configuração do repositório [y]{file}[.] contém erros de YAML e está [r]corrompido[.].\\nErro: {error}\\nAbra e corrija o conteúdo ou crie um novo.",
        "repository_loader.config_empty": "O arquivo de configuração do repositório [y]{file}[.] está [r]vazio[.].\\nAbra e corrija o conteúdo ou crie um novo.",
        "repository_loader.config_corrupted_unexpected": "O arquivo de configuração do repositório [y]{file}[.] está [r]corrompido[.].\\nErro inesperado: {error}\\nAbra e corrija o conteúdo ou crie um novo.",
        "lang_select.default_not_set": "Linguagem padrão ainda não foi definida.",
        "lang_select.prompt": "Escolha entre as opções a seguir",
        "lang_select.options_prefix": "[",
        "lang_select.options_suffix": "]",
        "remote.edit_hint": "Você também pode configurar as fontes e filtros manualmente editando o arquivo:",
        "remote.none_configured": "Nenhuma fonte configurada",
        "remote.configured_sources": "Fontes configuradas:",
        "remote.label": "- Rótulo:",
        "remote.link": "- Link ou Caminho:",
        "remote.index": "- Índice:",
        "remote.quest_filter": "- Filtro Quests:",
        "remote.filter_disabled": "Desativado",
        "remote.filter_enabled": "Ativado",
        "remote.removed_success": "Fonte {alias} removida com sucesso.",
        "remote.not_found": "fail: fonte não encontrada.",
        "remote.filters_updated": "Filtros {alias} atualizados com sucesso.",
        "remote.name_exists": "fail: fonte com esse nome já existe.",
        "remote.adding_git": "Adicionando fonte remota apontando para repositório git remoto {url}",
        "remote.git_alias_not_found": "fail: alias git remoto não encontrado.",
        "remote.clone_error": "Erro ao clonar repositório, fonte não foi adicionada",
        "remote.clone_failed": "fail: não foi possível clonar o repositório.",
        "remote.dir_not_found": "fail: diretório remoto não encontrado.",
        "remote.adding_local": "Adicionando fonte remota apontando para o repositório no diretório {path}",
        "remote.adding_url": "Adicionando fonte remota apontando para repositório git remoto {url}",
        "remote.added_success": "Fonte remota {name} adicionada com sucesso.",
        "remote.cloning": "Clonando repositório remoto {link}",
        "remote.cloned_success": "Repositório {link} clonado com sucesso.",
        "remote.can_access": "Você pode acessar o repositório com o comando [g]tko open[.]",
        "pull.unexpected_error": "Erro inesperado ao executar comando git em {directory}",
        "pull.up_to_date": "Up-to-date",
        "pull.fetch_label": "Fetch",
        "pull.fetch_failed": "Fetch failed: {msg}",
        "pull.update_label": "Update",
        "pull.fallback_label": "Fallback",
        "pull.reset_failed": "Reset failed: {msg}",
        "pull.all_parallel": "Pull de {count} repositórios ({threads} threads)",
        "pull.error_in_repo": "Erro ao fazer pull em {repo}",
        "pull.completed": "Finalizado em {elapsed:.2f}s",
        "cli.common.global_cache": "Usando cache global em: {cache}",
        "cli.common.no_repo": "Nenhum repositório TKO encontrado.",
        "cli.tool.mdpp_updating_readme": "Atualizando README.md em {folder}",
        "cli.tool.rebase_url_downloaded": "Arquivo url={url} baixado com sucesso",
        "cli.tool.rebase_done": "Rebase concluído",
        "cli.tool.rebase_saved_path": "Arquivo salvo no path: {path}",
        "cli.tool.rebase_alias_readme_failed": "Não foi possível baixar README.md para @{alias}: {error}",
        "cli.tool.html_input_md_required": "Erro: O arquivo de entrada Markdown deve ter a extensão .md",
        "cli.tool.html_output_html_required": "Erro: O arquivo de saída HTML deve ter a extensão .html",
        "cmd.build_execute_failed": "Falha ao executar o build para {target}",
        "cmd.collect_repo_not_found": "Repositório não encontrado em {path}",
        "cmd.collect_tko_repo_not_found": "Repositório TKO não encontrado em {path}",
        "cmd.collect_multiple_repos_found": " - Múltiplos repositórios TKO encontrados, usando o primeiro.",
        "cmd.collect_running_in": "Executando tko collect em {folder}",
        "cmd.collect_json_parse_failed": "Erro: Falha ao analisar saída JSON para {username}",
        "cmd.collect_error": "Erro: {error}",
        "cmd.collect_saving_extracted_data": "Salvando dados extraídos em {path}",
        "cmd.down_activity_link_not_downloadable": "Atividade {task_key} é do tipo link, ela não é para download",
        "cmd.down_activity_no_origin_folder": "Atividade {task_key} não possui pasta de origem para download",
        "cmd.down_activity_no_destiny_folder": "Atividade {task_key} não possui pasta de destino para download",
        "cli.config_settings_file": "SettingsFile\\n- {settings_dir}",
        "cli.remote_clear_with_quest_error": "Erro: --clear não pode ser usado com --quest",
        "cli.build_updating_drafts": "Atualizando drafts em {folder}",
        "writer.no_changes_test_file": "no changes in test file",
        "writer.file_wrote": "file {path} wrote",
        "writer.target_not_supported_build": "fail: target {target} do not supported for build operation",
        "task.code_not_found": "O arquivo de código não foi encontrado.",
        "task.code_only_downloaded": "Você só pode abrir o código de tarefas baixadas.",
        "task.opening_link": "Abrindo link",
        "task.is_mission": "Essa é uma missão.",
        "task.link_only_tasks": "Você só pode abrir o link de tarefas.",
        "task.versions_decompressed": "As versões da tarefa foram descompactadas em uma pasta temporária",
        "task.versions_opening": "Abrindo com o comando: {cmd}",
        "task.download_is_mission": "Essa é uma missão.",
        "task.download_only_tasks": "Você só pode baixar tarefas.",
        "task.download_not_importable": "Essa não é uma tarefa de baixável.",
        "task.download_header": "Baixando tarefa",
        "task.delete_not_match": "Texto digitado não corresponde ao identificador da tarefa.",
        "task.delete_success": "Pasta {folder} apagada com sucesso.",
        "play.action.delete_error": "Erro ao apagar pasta.",
        "play.palette.down_task": "Tarefa",
        "play.palette.evaluate": "Tarefa",
        "play.palette.delete": "Tarefa",
        "play.palette.help": "Mostrar",
        "play.palette.borders": "Mostrar",
        "play.palette.images": "Mostrar",
        "play.palette.time": "Mostrar",
        "play.palette.language": "Mudar",
        "play.palette.calibrate": "Calibrar",
        "play.palette.draft": "Criar",
        "play.palette.reload": "Reload",
        "play.palette.versions": "Ver",
        "play.palette.panel_size": "Painel",
        "loader.failed_to_load": "Falha ao carregar arquivos da pasta {folder}",
        "gui_top_bar.recommended": "Recomendadas",
        "gui_top_bar.all": "Todas",
        "gui_top_bar.graphs": "Gráficos",
        "gui_top_bar.logs": "Logs",
        "gui_top_bar.skills": "Trilhas",
        "gui_top_bar.help": "Ajuda",
        "gui_top_bar.exec": "Exec",
        "gui_top_bar.time": "Time",
        "tester.task_folder_not_found": "Warning: Pasta da tarefa não encontrada",
        "tester_top_bar.running_locked_activity": "Executando atividade travada",
        "tester_top_bar.no_tests_registered": "Nenhum teste cadastrado",
        "tester_top_bar.compile_error": "Erro de compilação",
        "tester_navigator.locked_hint": "{arrow}\nAtividade travada\nAperte {lock_key} para destravar",
        "tester_navigator.single_solver_1": "Seu projeto só tem um arquivo de solução.",
        "tester_navigator.single_solver_2": "Essa funcionalidade troca qual dos arquivos",
        "tester_navigator.single_solver_3": "de solução será o principal.",
        "tester_navigator.no_log_repo": "Nenhum repositório de logs encontrado.",
        "tester.compile_error_during_run": "CompileError durante execução do tester",
        "tester.press_enter_to_continue": "Pressione enter para continuar",
        "task.download_is_mission": "Essa é uma missão.",
        "task.download_only_tasks": "Você só pode baixar tarefas.",
        "task.download_not_importable": "Essa não é uma tarefa de bai xável.",
        "task.download_header": "Baixando tarefa",
        "task.delete_not_match": "Texto digitado não corresponde ao identificador da tarefa.",
        "task.delete_success": "Pasta {folder} apagada com sucesso.",
        "play.action.delete_error": "Erro ao apagar pasta.",
        "play.palette.down_task": "Tarefa",
        "play.palette.evaluate": "Tarefa",
        "play.palette.delete": "Tarefa",
        "play.palette.help": "Mostrar",
        "play.palette.borders": "Mostrar",
        "play.palette.images": "Mostrar",
        "play.palette.time": "Mostrar",
        "play.palette.language": "Mudar",
        "play.palette.calibrate": "Calibrar",
        "play.palette.draft": "Criar",
        "play.palette.reload": "Reload",
        "play.palette.versions": "Ver",
        "play.palette.panel_size": "Painel",
    },
    "en": {
        "app.version": "tko {version}",
        "app.context_not_set": "Error: App context is not properly set.",
        "app.keyboard_interrupt": "Keyboard Interrupt",
        "repo_starter.language_set": "Repository language set to [y]{language}[.].",
        "repo_starter.open_hint": "You can access the repository with the command [g]tko open[.]",
        "repo_starter.exists": "A TKO repository already exists in folder [y]{folder}[.]",
        "repo_starter.reset_prompt": "Do you want to reset the repository? ([g]y[.]/[r]n[.]): ",
        "repo_starter.inside_other_repo": "You are trying to create a repository inside another one, because there is already a repo in [r]{parent}[.]",
        "repo_starter.overwrite_prompt": "Do you want to overwrite the repository settings in [y]{folder}[.] ? ([g]y[.]/[r]n[.]): ",
        "repo_starter.deep_repo_warn": "You are trying to create a TKO repository in folder [y]{folder}[.]",
        "repo_starter.deep_repo_warn_2": "But there are already TKO repositories below that folder. Move or delete them",
        "repo_starter.empty_repo": "Creating empty repository, as a folder for local activities",
        "reset.no_repo": "No TKO repository found.",
        "reset.settings_path": "Global settings file:",
        "reset.languages_path": "Language settings:",
        "open.invalid_repo": "[r]Error[.]: The [g]tko open[.] command must run in the folder where the repository was initialized.",
        "open.action_hint": "[g]Action[.]: Navigate to that folder or pass its path and try again.",
        "down.invalid_repo_arg": "The argument for tko down must be the folder where you initialized the repository.",
        "down.invalid_repo_arg_action": "Navigate to that folder or pass its path and try again.",
        "down.activity_already_present": "Activity is already in the repository; no files need to be downloaded",
        "down.link_has_no_download": "fail: activity link does not provide a download link",
        "down.creating_new_draft_folder": "Creating new drafts folder: {folder}",
        "down.copy_new_drafts_manually": "If you want to use the new drafts, copy them manually",
        "down.copy_new_drafts_to_lang": "the new drafts to folder {lang}",
        "down.latest_draft": "Latest draft in {name}",
        "down.activity_downloaded_success": "Activity downloaded successfully",
        "down.choose_draft_extension": "Choose a draft extension: [{options}]: ",
        "down.file_new": "{path} (New)",
        "down.file_updated": "{path} (Updated)",
        "down.file_unchanged": "{path} (Unchanged)",
        "down.file_empty": "{path} (Empty)",
        "down.file_not_overwritten": "{path} (Not overwritten)",
        "grade.header": " Use arrow keys and text to mark",
        "grade.footer": " Press Enter to confirm, Esc to cancel",
        "grade.auto_mode_label": "Percentage of tests that passed in the last run:",
        "grade.manual_mode_label": "What percentage of the activity did you complete?",
        "grade.study_time_label": "What is the total estimated time, study + code, in minutes?",
        "grade.friend_label": "Leave blank if you did it alone, or with the name of who helped",
        "grade.guided_label": "Did you code by copying from class or video?",
        "grade.guided_discount": "COPIED:",
        "grade.concept_label": "STUDY concepts without generating the problem solution?",
        "grade.concept_discount": "STUDY:",
        "grade.problem_label": "UNDERSTAND the problem to be solved?",
        "grade.problem_discount": "UNDERSTAND:",
        "grade.code_label": "GENERATE or FIX code related to the problem?",
        "grade.code_discount": "FIX:",
        "grade.debug_label": "UNDERSTAND ERROR messages or incorrect OUTPUT?",
        "grade.debug_discount": "DEBUG:",
        "grade.refactor_label": "REFACTOR code only after doing everything yourself?",
        "grade.refactor_discount": "REFACTOR:",
        "grade.section_title": "Rate according to the last time you (re)did the task from scratch (sprint)",
        "grade.section_human_help": "Did you do it with human help or guided?",
        "grade.section_ai_usage": "Did you use AI (LLMs) for",
        "grade.yes": "Yes",
        "grade.no": "No",
        "grade.nothing": " Nothing",
        "gui_left_panel.search": " Search: ",
        "gui_left_panel.outdated": " TKO OUTDATED!",
        "gui_left_panel.update_message": " Update with: ",
        "gui_left_panel.update_command": "pipx upgrade tko ",
        "calibrate.left": "Left",
        "calibrate.right": "Right",
        "calibrate.up": "Up",
        "calibrate.down": "Down",
        "calibrate.esc": "Esc",
        "calibrate.page_up": "PageUp",
        "calibrate.page_down": "PageDown",
        "calibrate.backspace": "Backspace",
        "input_text.prompt": "Type here: ",
        "run.testing_label": " Testing code with test cases ",
        "run.no_source_files": "No source files found.",
        "run.no_source_or_tests": "No source files or tests found.",
        "run.no_test_cases": "No test cases found.",
        "run.no_code_found": "No source files found. Listing test cases.",
        "run.pack_load_failed": "Failed to load unit pack from {source}",
        "run.autoload_folder_not_set": "fail: autoload folder is not set",
        "run.autoload_lang_hint": "You did not define files directly. Use [y]-l[.] if you want to specify the language for autoloading.",
        "run.filter_index_out_of_bounds": "Index out of bounds: {index}",
        "run.task_not_defined": "Task not defined",
        "run.target_not_found": "fail: {target} not found",
        "solver.command_not_found": "fail: command '{name}' was not found",
        "solver.extension_unrecognized": "Fail: File extension '{suffix}' not recognized and no language configuration found",
        "solver.ts_config_not_found": "Fail: Language configuration for 'ts' not found",
        "config.borders_status": "Borders now is: {status}",
        "config.images_status": "Images now is: {status}",
        "config.diff_mode_side": "Diff mode now is: SIDE_BY_SIDE",
        "config.diff_mode_down": "Diff mode now is: UP_DOWN",
        "config.editor_changed": "New command to open source files: {editor}",
        "config.timeout_changed": "New timeout: {timeout}",
        "config.lang_empty": "Language settings are empty",
        "config.lang_load_failed": "Error loading language settings {path}, resetting to default settings",
        "settings.git_label_not_found": "Git repository label {alias} not found",
        "settings.empty_config_file": "Empty config file: {path}",
        "settings.remote_sources_registered": "Registered remote task sources:",
        "game_builder.readme_fetch_error": "Error fetching README file from source {name}",
        "game_builder.source_not_found": "Warning: source {filename} not found in source {name}",
        "game_builder.source_not_found_creating": "Warning: source {filename} not found in source {name}, creating file",
        "game_builder.source_no_origin_dir": "Warning: source {name} has no source directory",
        "game_builder.index_fetch_error": "Error fetching index file from source {name}",
        "game_builder.quest_requires_missing": "Quest\\n{filename}:{line}\\n{quest}\\nrequires {required} that does not exist",
        "game_builder.no_quest_title": "No Quest",
        "game.task_not_found_in_course": "fail: task '{task_key}' not found in course",
        "game.build_failed_for_source": "Failed to build game for source {name}",
        "loader.target_format_not_supported": "warning: target format is not supported: {source}",
        "loader.unable_to_find": "warning: unable to find: {source}",
        "toml.case_invalid": "Case {index} is invalid.",
        "toml.case_data_warning": "warning: case {index} data: {case}",
        "mdpp.missing_extract_value": "missing value for --extract",
        "mdpp.invalid_tests_integer": "invalid or missing integer for --tests",
        "mdpp.unrecognized_tag": "unrecognized tag '{tag}'",
        "mdpp.file_not_found": "file {path} not found",
        "mdpp.file_updated": "file {path} updated",
        "mdpp.file_not_markdown": "File {path} is not a markdown file",
        "feno_html.markdown_not_found": "Error: Markdown file not found at '{path}'",
        "feno_html.conversion_error": "An error occurred during conversion",
        "feno_build.no_target_specified": "No target specified, using current directory",
        "feno_build.target_not_directory": "fail: {target} is not a directory",
        "feno_github_cfg.not_set": "fail: {filename} file not set",
        "game.sandbox_source_not_found": "Local sandbox source not found",
        "run.filter_mode_banner": " Entering filter mode ",
        "repository_data.load_error": "Error loading data from dictionary",
        "remote.git_cache_root_required": "Git cache and root dir must be set to resolve the path",
        "remote.sandbox_only_true": "Sandbox source can only be set to True",
        "remote_path.source_dir_not_exists": "Source directory does not exist",
        "remote_path.index_file_not_exists": "Index file does not exist",
        "game_coordinator.loading_repository": "Loading repository from {root}...",
        "task_parser.view_external_url": "Parsing view task with external url: {url}",
        "task_parser.edit_external_url": "Parsing edit task with external url: {url}",
        "pattern.wildcard_only_once": "  fail: the wildcard @ should be used only once per pattern",
        "pattern.input_wildcard_requires_output": "  fail: if input_pattern has wildcard @, output_pattern should have it too",
        "pattern.output_wildcard_requires_input": "  fail: if output_pattern has wildcard @, input_pattern should have it too",
        "pattern.output_file_not_found": "fail: file {file} not found",
        "indexer.invalid_label": "Invalid label in line: {label}",
        "indexer.found_readmes": "Found {count} README.md files in base directory '{base_dir}'",
        "indexer.missing_readme_removing": "Warning: README file '[y]{readme}[.]' does not exist for task:[b]{task}[.], removing from index",
        "indexer.missing_readme_task": "Warning: README file '[y]{readme}[.]' does not exist for task:[b]{task}[.]",
        "indexer.mismatch_title": "Mismatch title for task:[b]{readme}[.]\n\tREADME:'[y]{line_title}[.]' != TASK:'[g]{folder_title}[.]'",
        "indexer.replace_title_readme_missing": "Error: README file '{readme}' does not exist, cannot replace title.",
        "indexer.replaced_title": "Replaced title in '{readme}' with '{title}'",
        "indexer.missing_hooks_adding": "Found {count} missing hooks, adding to quest '{quest}':",
        "collected.no_resume_data": "No resume data found in the JSON.",
        "floating.invalid_align": "Invalid align {align}",
        "task_editor.opening_link_log": "Opening link for task: {task_key}, URL: {url}",
        "task_editor.target_log": "Target: {target}",
        "cli.remote_add_source_error": "Error adding source",
        "label_factory.index_int_required": "Index on label must be a integer",
        "github_url.invalid_url": "Invalid URL",
        "github_url.invalid_github_url": "Invalid GitHub URL",
        "execution_result.invalid_type": "Invalid result type",
        "filter.file_not_found": "Warning: File {path} not found",
        "filter.target_must_be_folder": "Error: target must be a folder in recursive mode",
        "filter.output_folder_required": "Error: output folder must be specified in recursive mode",
        "filter.output_folder_exists": "Error: output folder already exists",
        "filter.action_path": "action: {action}, path: {path}",
        "filter.action_disabled_path": "action: disabled, path: {path}",
        "git_cache.clearing": "Clearing git cache at {cache_dir}...",
        "git_cache.cloning": "Cloning {url} into cache...",
        "git_cache.clone_failed": "Failed to clone {url}. Removing cache directory...",
        "git_cache.updating": "Updating cache for {url}...",
        "git_cache.update_failed_reclone": "Failed to update cache for {url}. Removing and re-cloning...",
        "grading.readme_not_found": "README file '{file}' does not exist.",
        "grading.no_problems_found": "No problems found in the configuration file.",
        "grading.running_prefix": "[TKO RUNNING] ",
        "grading.grading_prefix": "[TKO GRADING] ",
        "tracker.not_enough_columns": "Not enough columns to create a Track object.",
        "tracker.invalid_timestamp_format": "Invalid timestamp format: {timestamp}. Expected format is YYYY-MM-DD_HH-MM-SS.",
        "logger.invalid_item_type": "Invalid Item Type",
        "logger.log_folder_not_dir": "Log folder '{log_folder}' is not a directory.",
        "logger.unknown_action": "Unknown action {action}",
        "fmt.not_initialized": "Fmt.__scr was not initialized",
        "input.duplicate_key": "Duplicate key {input_key}",
        "task_launcher.folder_not_found": "Folder not found",
        "task_launcher.no_source_for_lang": "No source file found for language {lang}.",
        "task_launcher.draft_created": "A draft file was created",
        "play.key_not_recognized": "Key char:{char}, code:{code}, not recognized",
        "draft_creator.title_prompt": "Type the Title (use @label to define the key manually)",
        "draft_creator.title_placeholder": "Type task title here",
        "draft_creator.folder_exists": "Folder {folder} already exists.",
        "draft_creator.created_at": "Draft created at {folder}",
        "play_action.task_no_local_folder": "This task does not have a local code folder.",
        "play_action.only_task_folders": "You can only delete task folders.",
        "play_action.delete_confirm_prefix": "To delete this folder, type ",
        "game_validator.duplicate_key": "Duplicate key: {task_key}",
        "game_validator.self_ref_error": "Error: self reference {line_number} {line}",
        "game_validator.cycle_detected": "Cycle detected: {visited}",
        "task_path.view_no_workdir": "Task {task_key} is a view resource, it does not have a work directory",
        "task_path.invalid_local_path": "Task {task_key} does not have a valid local path",
        "freerun.prompt_rerun": "Press enter to recompile and rerun",
        "freerun.prompt_back": "To go back, type q and press enter",
        "text.must_be_string": "text must be a string",
        "text.index_out_of_range": "index out of range",
        "repository_loader.git_conflict": "Git merge conflict detected in {file}.\\nPlease resolve the conflict manually before continuing.",
        "repository_loader.empty_config_file": "Empty config file: {file}",
        "repository_loader.yaml_corrupted": "The repository configuration file [y]{file}[.] contains YAML errors and is [r]corrupted[.].\\nError: {error}\\nOpen and fix the content or create a new one.",
        "repository_loader.config_empty": "The repository configuration file [y]{file}[.] is [r]empty[.].\\nOpen and fix the content or create a new one.",
        "repository_loader.config_corrupted_unexpected": "The repository configuration file [y]{file}[.] is [r]corrupted[.].\\nUnexpected error: {error}\\nOpen and fix the content or create a new one.",
        "lang_select.default_not_set": "Default language has not been set yet.",
        "lang_select.prompt": "Choose from the following options",
        "lang_select.options_prefix": "[",
        "lang_select.options_suffix": "]",
        "remote.edit_hint": "You can also configure sources and filters manually by editing the file:",
        "remote.none_configured": "No sources configured",
        "remote.configured_sources": "Configured sources:",
        "remote.label": "- Label:",
        "remote.link": "- Link or Path:",
        "remote.index": "- Index:",
        "remote.quest_filter": "- Quest Filter:",
        "remote.filter_disabled": "Disabled",
        "remote.filter_enabled": "Enabled",
        "remote.removed_success": "Source {alias} removed successfully.",
        "remote.not_found": "fail: source not found.",
        "remote.filters_updated": "Filters for {alias} updated successfully.",
        "remote.name_exists": "fail: a source with this name already exists.",
        "remote.adding_git": "Adding remote source pointing to git repository {url}",
        "remote.git_alias_not_found": "fail: remote git alias not found.",
        "remote.clone_error": "Error cloning repository, source was not added",
        "remote.clone_failed": "fail: could not clone the repository.",
        "remote.dir_not_found": "fail: remote directory not found.",
        "remote.adding_local": "Adding remote source pointing to repository in directory {path}",
        "remote.adding_url": "Adding remote source pointing to git repository {url}",
        "remote.added_success": "Remote source {name} added successfully.",
        "remote.cloning": "Cloning remote repository {link}",
        "remote.cloned_success": "Repository {link} cloned successfully.",
        "remote.can_access": "You can access the repository with the command [g]tko open[.]",
        "pull.unexpected_error": "Unexpected error executing git command in {directory}",
        "pull.up_to_date": "Up-to-date",
        "pull.fetch_label": "Fetch",
        "pull.fetch_failed": "Fetch failed: {msg}",
        "pull.update_label": "Update",
        "pull.fallback_label": "Fallback",
        "pull.reset_failed": "Reset failed: {msg}",
        "pull.all_parallel": "Pull of {count} repositories ({threads} threads)",
        "pull.error_in_repo": "Error pulling from {repo}",
        "pull.completed": "Completed in {elapsed:.2f}s",
        "cli.common.global_cache": "Using global cache at: {cache}",
        "cli.common.no_repo": "No TKO repository found.",
        "cli.tool.mdpp_updating_readme": "Updating README.md in {folder}",
        "cli.tool.rebase_url_downloaded": "File url={url} downloaded successfully",
        "cli.tool.rebase_done": "Rebase completed",
        "cli.tool.rebase_saved_path": "File saved at path: {path}",
        "cli.tool.rebase_alias_readme_failed": "Could not download README.md for @{alias}: {error}",
        "cli.tool.html_input_md_required": "Error: Input Markdown file must have the .md extension",
        "cli.tool.html_output_html_required": "Error: Output HTML file must have the .html extension",
        "cmd.build_execute_failed": "Failed to execute build for {target}",
        "cmd.collect_repo_not_found": "Repository not found in {path}",
        "cmd.collect_tko_repo_not_found": "TKO repo not found in {path}",
        "cmd.collect_multiple_repos_found": " - Multiple TKO repos found, using the first one.",
        "cmd.collect_running_in": "Running tko collect in {folder}",
        "cmd.collect_json_parse_failed": "Error: Failed to parse JSON output for {username}",
        "cmd.collect_error": "Error: {error}",
        "cmd.collect_saving_extracted_data": "Saving extracted data to {path}",
        "cmd.down_activity_link_not_downloadable": "Activity {task_key} is a link type and is not downloadable",
        "cmd.down_activity_no_origin_folder": "Activity {task_key} has no source folder for download",
        "cmd.down_activity_no_destiny_folder": "Activity {task_key} has no destination folder for download",
        "cli.config_settings_file": "SettingsFile\\n- {settings_dir}",
        "cli.remote_clear_with_quest_error": "Error: --clear cannot be used with --quest",
        "cli.build_updating_drafts": "Updating drafts in {folder}",
        "writer.no_changes_test_file": "no changes in test file",
        "writer.file_wrote": "file {path} wrote",
        "writer.target_not_supported_build": "fail: target {target} do not supported for build operation",
        "task.code_not_found": "Code file not found.",
        "task.code_only_downloaded": "You can only open code from downloaded tasks.",
        "task.opening_link": "Opening link",
        "task.is_mission": "This is a mission.",
        "task.link_only_tasks": "You can only open the link for tasks.",
        "task.versions_decompressed": "Task versions have been decompressed to a temporary folder",
        "task.versions_opening": "Opening with command: {cmd}",
        "task.download_is_mission": "This is a mission.",
        "task.download_only_tasks": "You can only download tasks.",
        "task.download_not_importable": "This is not a downloadable task.",
        "task.download_header": "Downloading task",
        "task.delete_not_match": "Entered text does not match the task identifier.",
        "task.delete_success": "Folder {folder} deleted successfully.",
        "play.action.delete_error": "Error deleting folder.",
        "play.palette.down_task": "Task",
        "play.palette.evaluate": "Task",
        "play.palette.delete": "Task",
        "play.palette.help": "Show",
        "play.palette.borders": "Show",
        "play.palette.images": "Show",
        "play.palette.time": "Show",
        "play.palette.language": "Change",
        "play.palette.calibrate": "Calibrate",
        "play.palette.draft": "Create",
        "play.palette.reload": "Reload",
        "play.palette.versions": "View",
        "play.palette.panel_size": "Panel",
        "loader.failed_to_load": "Failed to load files from folder {folder}",
        "gui_top_bar.recommended": "Recommended",
        "gui_top_bar.all": "All",
        "gui_top_bar.graphs": "Graphs",
        "gui_top_bar.logs": "Logs",
        "gui_top_bar.skills": "Skills",
        "gui_top_bar.help": "Help",
        "gui_top_bar.exec": "Exec",
        "gui_top_bar.time": "Time",
        "tester.task_folder_not_found": "Warning: Task folder not found",
        "tester_top_bar.running_locked_activity": "Running locked activity",
        "tester_top_bar.no_tests_registered": "No tests registered",
        "tester_top_bar.compile_error": "Compilation error",
        "tester_navigator.locked_hint": "{arrow}\nLocked activity\nPress {lock_key} to unlock",
        "tester_navigator.single_solver_1": "Your project has only one solution file.",
        "tester_navigator.single_solver_2": "This feature switches which solution file",
        "tester_navigator.single_solver_3": "will be used as the main one.",
        "tester_navigator.no_log_repo": "No log repository found.",
        "tester.compile_error_during_run": "CompileError during tester run",
        "tester.press_enter_to_continue": "Press Enter to continue",
        "task.download_is_mission": "This is a mission.",
        "task.download_only_tasks": "You can only download tasks.",
        "task.download_not_importable": "This is not a downloadable task.",
        "task.download_header": "Downloading task",
        "task.delete_not_match": "Entered text does not match the task identifier.",
        "task.delete_success": "Folder {folder} deleted successfully.",
        "play.action.delete_error": "Error deleting folder.",
        "play.palette.down_task": "Task",
        "play.palette.evaluate": "Task",
        "play.palette.delete": "Task",
        "play.palette.help": "Show",
        "play.palette.borders": "Show",
        "play.palette.images": "Show",
        "play.palette.time": "Show",
        "play.palette.language": "Change",
        "play.palette.calibrate": "Calibrate",
        "play.palette.draft": "Create",
        "play.palette.reload": "Reload",
        "play.palette.versions": "View",
        "play.palette.panel_size": "Panel",
    },
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
    env_language = os.environ.get("TKO_LANG") or os.environ.get("LANG") or os.environ.get("LC_ALL")
    return normalize_language(env_language)


def set_language(language: str | None) -> str:
    global _current_language
    _current_language = normalize_language(language)
    return _current_language


def get_catalog_keys(language: str) -> set[str]:
    normalized = normalize_language(language)
    return set(_TRANSLATIONS.get(normalized, _TRANSLATIONS["pt-BR"]).keys())


def t(key: MsgKey, **params: Any) -> str:
    key_value = key.value
    language = get_language()
    catalog = _TRANSLATIONS.get(language, _TRANSLATIONS["pt-BR"])
    template = catalog.get(key_value, _TRANSLATIONS["pt-BR"].get(key_value, key_value))
    return template.format(**params)
