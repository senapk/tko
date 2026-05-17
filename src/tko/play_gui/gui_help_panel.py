from tko.widget.frame import Frame
from tko.play.keys import GuiKeys
from tko.i18n import MsgKey, t
from tko.util.rtext import RText
from tko.util.symbols import Symbols


class GuiHelpPanel:

    def show(self, frame: Frame) -> None:
        frame.draw()
        dx = frame.get_dx() - 2
        help_lines: list[RText] = []
        help_lines.append(RText.format("{g}", t(MsgKey.GUI_HELP_SECTION_CONFIG)).center(dx, RText("-")))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_BORDERS_LINE), "B", "", t(MsgKey.GUI_HELP_BORDERS_DESC), ""))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_CALIBRATE_LINE), GuiKeys.calibrate))

        help_lines.append(RText(t(MsgKey.GUI_HELP_SECTION_SYMBOLS), "g").center(dx, RText("-")))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_SYMBOL_SUGGESTED_OPTIONAL), Symbols.star_filled, Symbols.star_void))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_SYMBOL_STUDY_WRITE_NOHELP), Symbols.loss_free, Symbols.loss_part, Symbols.loss_zero))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_SYMBOL_SELF_EVAL),
                                       Symbols.diamond_filled, Symbols.circle_filled, Symbols.task_view,
                                       Symbols.diamond_void, Symbols.circle_void, Symbols.task_view))
        help_lines.append(RText.format("{g}", t(MsgKey.GUI_HELP_SECTION_NAVIGATION)).center(dx, RText("-")))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_NAV_ARROWS), "↑↓→"))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_NAV_ENTER), "↲"))
        help_lines.append(RText(t(MsgKey.GUI_HELP_SECTION_INTERFACE), "g").center(dx, RText("-")))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_INTERFACE_INBOX), GuiKeys.inbox))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_INTERFACE_ALL), GuiKeys.all_tasks))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_INTERFACE_PALETTE), GuiKeys.palette))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_INTERFACE_TIME), GuiKeys.show_duration))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_INTERFACE_SEARCH), GuiKeys.search))

        help_lines.append(RText(t(MsgKey.GUI_HELP_SECTION_TASKS), "g").center(dx, RText("-")))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_TASK_DOWNLOAD), GuiKeys.down_task))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_TASK_DELETE), GuiKeys.delete_folder))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_TASK_DRAFT), GuiKeys.create_draft))
        help_lines.append(RText.format(t(MsgKey.GUI_HELP_TASK_EVALUATION), GuiKeys.self_evaluate))

        help_lines.append(RText.format("{g}", t(MsgKey.GUI_HELP_SECTION_DEFAULT_EDITOR)).center(dx, RText("-")))
        help_lines.append(RText(t(MsgKey.GUI_HELP_EDITOR_DESC)))
        help_lines.append(RText(t(MsgKey.GUI_HELP_EDITOR_COMMAND), "y").center(dx))

        for i, line in enumerate(help_lines):
            frame.write(i, 0, line)
