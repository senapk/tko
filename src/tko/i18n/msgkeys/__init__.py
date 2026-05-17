from __future__ import annotations

from enum import Enum
from typing import Any

from tko.i18n.msgkeys.cli import CliMsgKey
from tko.i18n.msgkeys.config import ConfigMsgKey
from tko.i18n.msgkeys.core import CoreMsgKey
from tko.i18n.msgkeys.down import DownMsgKey
from tko.i18n.msgkeys.feno import FenoMsgKey
from tko.i18n.msgkeys.game import GameMsgKey
from tko.i18n.msgkeys.gui import GuiMsgKey
from tko.i18n.msgkeys.misc import MiscMsgKey
from tko.i18n.msgkeys.play import PlayMsgKey
from tko.i18n.msgkeys.repository import RepositoryMsgKey
from tko.i18n.msgkeys.run import RunMsgKey
from tko.i18n.msgkeys.tester import TesterMsgKey

_MSGKEY_ENUMS: tuple[type[Enum], ...] = (
    CliMsgKey,
    ConfigMsgKey,
    CoreMsgKey,
    DownMsgKey,
    FenoMsgKey,
    GameMsgKey,
    GuiMsgKey,
    MiscMsgKey,
    PlayMsgKey,
    RepositoryMsgKey,
    RunMsgKey,
    TesterMsgKey,
)


def _build_msg_key_enum() -> type[Enum]:
    members: dict[str, str] = {}
    duplicates: list[str] = []

    for enum_cls in _MSGKEY_ENUMS:
        for name, member in enum_cls.__members__.items():
            if name in members:
                duplicates.append(name)
                continue
            members[name] = member.value

    if duplicates:
        unique = ", ".join(sorted(set(duplicates)))
        raise RuntimeError(f"Duplicate i18n MsgKey names across modules: {unique}")

    return Enum("MsgKey", members, type=str)


MsgKey: Any = _build_msg_key_enum()

__all__ = [
    "MsgKey",
    "CliMsgKey",
    "ConfigMsgKey",
    "CoreMsgKey",
    "DownMsgKey",
    "FenoMsgKey",
    "GameMsgKey",
    "GuiMsgKey",
    "MiscMsgKey",
    "PlayMsgKey",
    "RepositoryMsgKey",
    "RunMsgKey",
    "TesterMsgKey",
]
