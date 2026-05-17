from __future__ import annotations

from enum import Enum

class TesterMsgKey(str, Enum):
    TESTER_COMPILE_ERROR_DURING_RUN = 'tester.compile_error_during_run'
    TESTER_NAVIGATOR_LOCKED_HINT = 'tester_navigator.locked_hint'
    TESTER_NAVIGATOR_NO_LOG_REPO = 'tester_navigator.no_log_repo'
    TESTER_NAVIGATOR_SINGLE_SOLVER_1 = 'tester_navigator.single_solver_1'
    TESTER_NAVIGATOR_SINGLE_SOLVER_2 = 'tester_navigator.single_solver_2'
    TESTER_NAVIGATOR_SINGLE_SOLVER_3 = 'tester_navigator.single_solver_3'
    TESTER_PRESS_ENTER_TO_CONTINUE = 'tester.press_enter_to_continue'
    TESTER_TASK_FOLDER_NOT_FOUND = 'tester.task_folder_not_found'
    TESTER_TOP_BAR_COMPILE_ERROR = 'tester_top_bar.compile_error'
    TESTER_TOP_BAR_NO_TESTS_REGISTERED = 'tester_top_bar.no_tests_registered'
    TESTER_TOP_BAR_RUNNING_LOCKED_ACTIVITY = 'tester_top_bar.running_locked_activity'
