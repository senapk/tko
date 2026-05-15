from pathlib import Path

from tko.run.wdir_config import WdirConfig


def test_defaults_are_stable():
    cfg = WdirConfig()

    assert cfg.curses_mode is False
    assert cfg.lang == ""
    assert cfg.autoload is False
    assert cfg.autoload_folder is None


def test_setters_update_state_with_same_rules_as_wdir():
    cfg = WdirConfig()

    cfg.set_curses(True)
    cfg.set_lang("")
    cfg.set_lang("py")
    cfg.set_autoload_folder(Path("/tmp/x"))
    cfg.set_autoload(True)

    assert cfg.curses_mode is True
    assert cfg.lang == "py"
    assert cfg.autoload_folder == Path("/tmp/x")
    assert cfg.autoload is True
