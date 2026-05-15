# Re-export de compatibilidade — a definição canônica está em tko.config.flags
from tko.config.flags import (
    Flag,
    BoolFlag,
    ViewMode,
    PanelMode,
    TaskGraphMode,
    Flags,
)

__all__ = ["Flag", "BoolFlag", "ViewMode", "PanelMode", "TaskGraphMode", "Flags"]
