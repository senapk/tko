"""Textual presentation layer for the interactive TKO repository view."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tko.ui_textual.app import TkoApp

if TYPE_CHECKING:
    from tko.ui_textual.tester_app import TkoTesterApp
    from tko.ui_textual.dialogs import (
        ChoiceDialog, CommandPalette, ConfirmDialog, GradeDialog, GradeResult,
        PercentageSlider, StudyTimeSlider, TextInputDialog,
    )
    from tko.ui_textual.notifications import TextualNotifier


def __getattr__(name: str) -> object:
    if name == "TkoTesterApp":
        from tko.ui_textual.tester_app import TkoTesterApp

        return TkoTesterApp
    if name == "TextualNotifier":
        from tko.ui_textual.notifications import TextualNotifier

        return TextualNotifier
    if name in {
        "ChoiceDialog", "CommandPalette", "ConfirmDialog", "GradeDialog", "GradeResult",
        "PercentageSlider", "StudyTimeSlider", "TextInputDialog",
    }:
        from tko.ui_textual import dialogs

        return getattr(dialogs, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["TkoApp", "TkoTesterApp", "ChoiceDialog", "CommandPalette", "ConfirmDialog", "GradeDialog", "GradeResult", "PercentageSlider", "StudyTimeSlider", "TextInputDialog", "TextualNotifier"]
