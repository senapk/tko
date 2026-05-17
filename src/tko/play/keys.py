from enum import Enum

from tko.i18n import MsgKey, t


class _GuiActionsMeta(type):
    _KEY_MAP: dict[str, Enum] = {
        "create_draft": MsgKey("gui_action.create_draft"),
        "tab": MsgKey("gui_action.tab"),
        "leave": MsgKey("gui_action.leave"),
        "edit": MsgKey("gui_action.edit"),
        "show_time": MsgKey("gui_action.show_time"),
        "filter": MsgKey("gui_action.filter"),
        "principal": MsgKey("gui_action.principal"),
        "github": MsgKey("gui_action.github"),
        "help": MsgKey("gui_action.help"),
        "download": MsgKey("gui_action.download"),
        "activate": MsgKey("gui_action.activate"),
        "navigate": MsgKey("gui_action.navigate"),
        "uncheck": MsgKey("gui_action.uncheck"),
        "search": MsgKey("gui_action.search"),
        "pallete": MsgKey("gui_action.pallete"),
        "grade": MsgKey("gui_action.grade"),
        "time_limit": MsgKey("gui_action.time_limit"),
        "evaluate_tester": MsgKey("gui_action.evaluate_tester"),
        "execute_tester": MsgKey("gui_action.execute_tester"),
        "calibrate": MsgKey("gui_action.calibrate"),
        "draft": MsgKey("gui_action.draft"),
        "all": MsgKey("gui_action.all"),
    }

    def __getattr__(cls, name: str) -> str:
        key = cls._KEY_MAP.get(name)
        if key is not None:
            return t(key)
        raise AttributeError(name)


class GuiActions(metaclass=_GuiActionsMeta):
    pass

class GuiKeys:
    calibrate = "c"

    inbox = "1"
    all_tasks = "2"
    
    panel_graph = "3"
    panel_logs = "4"
    panel_skills = "5"
    panel_help = "6"
    panel_toggle = " "

    show_duration = "T"

    panel_resize_inc = ">"
    panel_resize_dec = "<"
    palette = "p"
    images = "I"
    down_task = "b"
    activate = "\n"
    reload_game = "R"
    
    expand_all = ']'
    collapse_all = "["
    create_draft = "r"
    set_lang_drafts = "L"
    toggle_ui_language = "P"
    open_url = "u"
    key_quit = "q"
    edit= "v"
    colors = "C"
    borders = "B"
    search = "/"
    self_evaluate = "a"
    self_evaluate_full = "A"
    delete_folder = "D"
    diff = "d"
    unfold_patch = "V"
    execute = "e"
    evaluate = "t"
    toggle_main = "\t"
    lock = "u"
    limite  = "l"
    expand = ">"
    collapse = "<"