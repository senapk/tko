from __future__ import annotations

from enum import Enum

class DownMsgKey(str, Enum):
    DOWN_ACTIVITY_ALREADY_PRESENT = 'down.activity_already_present'
    DOWN_ACTIVITY_DOWNLOADED_SUCCESS = 'down.activity_downloaded_success'
    DOWN_CHOOSE_DRAFT_EXTENSION = 'down.choose_draft_extension'
    DOWN_COPY_NEW_DRAFTS_MANUALLY = 'down.copy_new_drafts_manually'
    DOWN_COPY_NEW_DRAFTS_TO_LANG = 'down.copy_new_drafts_to_lang'
    DOWN_CREATING_NEW_DRAFT_FOLDER = 'down.creating_new_draft_folder'
    DOWN_FILE_EMPTY = 'down.file_empty'
    DOWN_FILE_NEW = 'down.file_new'
    DOWN_FILE_NOT_OVERWRITTEN = 'down.file_not_overwritten'
    DOWN_FILE_UNCHANGED = 'down.file_unchanged'
    DOWN_FILE_UPDATED = 'down.file_updated'
    DOWN_INVALID_REPO_ARG = 'down.invalid_repo_arg'
    DOWN_INVALID_REPO_ARG_ACTION = 'down.invalid_repo_arg_action'
    DOWN_LATEST_DRAFT = 'down.latest_draft'
    DOWN_LINK_HAS_NO_DOWNLOAD = 'down.link_has_no_download'
