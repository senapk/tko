from __future__ import annotations

from enum import Enum

class CliMsgKey(str, Enum):
    CLI_BUILD_UPDATING_DRAFTS = 'cli.build_updating_drafts'
    CLI_COMMON_GLOBAL_CACHE = 'cli.common.global_cache'
    CLI_COMMON_NO_REPO = 'cli.common.no_repo'
    CLI_CONFIG_SETTINGS_FILE = 'cli.config_settings_file'
    CLI_REMOTE_ADD_SOURCE_ERROR = 'cli.remote_add_source_error'
    CLI_REMOTE_CLEAR_WITH_QUEST_ERROR = 'cli.remote_clear_with_quest_error'
    CLI_TOOL_HTML_INPUT_MD_REQUIRED = 'cli.tool.html_input_md_required'
    CLI_TOOL_HTML_OUTPUT_HTML_REQUIRED = 'cli.tool.html_output_html_required'
    CLI_TOOL_MDPP_UPDATING_README = 'cli.tool.mdpp_updating_readme'
    CLI_TOOL_REBASE_ALIAS_README_FAILED = 'cli.tool.rebase_alias_readme_failed'
    CLI_TOOL_REBASE_DONE = 'cli.tool.rebase_done'
    CLI_TOOL_REBASE_SAVED_PATH = 'cli.tool.rebase_saved_path'
    CLI_TOOL_REBASE_URL_DOWNLOADED = 'cli.tool.rebase_url_downloaded'
    CMD_BUILD_EXECUTE_FAILED = 'cmd.build_execute_failed'
    CMD_COLLECT_ERROR = 'cmd.collect_error'
    CMD_COLLECT_JSON_PARSE_FAILED = 'cmd.collect_json_parse_failed'
    CMD_COLLECT_MULTIPLE_REPOS_FOUND = 'cmd.collect_multiple_repos_found'
    CMD_COLLECT_REPO_NOT_FOUND = 'cmd.collect_repo_not_found'
    CMD_COLLECT_RUNNING_IN = 'cmd.collect_running_in'
    CMD_COLLECT_SAVING_EXTRACTED_DATA = 'cmd.collect_saving_extracted_data'
    CMD_COLLECT_TKO_REPO_NOT_FOUND = 'cmd.collect_tko_repo_not_found'
    CMD_DOWN_ACTIVITY_LINK_NOT_DOWNLOADABLE = 'cmd.down_activity_link_not_downloadable'
    CMD_DOWN_ACTIVITY_NO_DESTINY_FOLDER = 'cmd.down_activity_no_destiny_folder'
    CMD_DOWN_ACTIVITY_NO_ORIGIN_FOLDER = 'cmd.down_activity_no_origin_folder'
