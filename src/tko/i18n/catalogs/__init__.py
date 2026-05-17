from __future__ import annotations

from tko.i18n.catalogs.cli import EN_TRANSLATIONS as _en_cli
from tko.i18n.catalogs.cli import PT_BR_TRANSLATIONS as _pt_cli
from tko.i18n.catalogs.config import EN_TRANSLATIONS as _en_config
from tko.i18n.catalogs.config import PT_BR_TRANSLATIONS as _pt_config
from tko.i18n.catalogs.core import EN_TRANSLATIONS as _en_core
from tko.i18n.catalogs.core import PT_BR_TRANSLATIONS as _pt_core
from tko.i18n.catalogs.down import EN_TRANSLATIONS as _en_down
from tko.i18n.catalogs.down import PT_BR_TRANSLATIONS as _pt_down
from tko.i18n.catalogs.feno import EN_TRANSLATIONS as _en_feno
from tko.i18n.catalogs.feno import PT_BR_TRANSLATIONS as _pt_feno
from tko.i18n.catalogs.game import EN_TRANSLATIONS as _en_game
from tko.i18n.catalogs.game import PT_BR_TRANSLATIONS as _pt_game
from tko.i18n.catalogs.gui import EN_TRANSLATIONS as _en_gui
from tko.i18n.catalogs.gui import PT_BR_TRANSLATIONS as _pt_gui
from tko.i18n.catalogs.misc import EN_TRANSLATIONS as _en_misc
from tko.i18n.catalogs.misc import PT_BR_TRANSLATIONS as _pt_misc
from tko.i18n.catalogs.play import EN_TRANSLATIONS as _en_play
from tko.i18n.catalogs.play import PT_BR_TRANSLATIONS as _pt_play
from tko.i18n.catalogs.repository import EN_TRANSLATIONS as _en_repository
from tko.i18n.catalogs.repository import PT_BR_TRANSLATIONS as _pt_repository
from tko.i18n.catalogs.run import EN_TRANSLATIONS as _en_run
from tko.i18n.catalogs.run import PT_BR_TRANSLATIONS as _pt_run
from tko.i18n.catalogs.tester import EN_TRANSLATIONS as _en_tester
from tko.i18n.catalogs.tester import PT_BR_TRANSLATIONS as _pt_tester

PT_BR_TRANSLATIONS: dict[str, str] = {
    **_pt_cli,
    **_pt_config,
    **_pt_core,
    **_pt_down,
    **_pt_feno,
    **_pt_game,
    **_pt_gui,
    **_pt_misc,
    **_pt_play,
    **_pt_repository,
    **_pt_run,
    **_pt_tester,
}

EN_TRANSLATIONS: dict[str, str] = {
    **_en_cli,
    **_en_config,
    **_en_core,
    **_en_down,
    **_en_feno,
    **_en_game,
    **_en_gui,
    **_en_misc,
    **_en_play,
    **_en_repository,
    **_en_run,
    **_en_tester,
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "pt-BR": PT_BR_TRANSLATIONS,
    "en": EN_TRANSLATIONS,
}
