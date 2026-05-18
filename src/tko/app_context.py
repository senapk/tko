from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

import logging
import typer
from tko.config.settings import Settings
from tko.i18n import Msg, t


logger = logging.getLogger(__name__)

_APP_CONTEXT_NOT_SET = Msg(
    pt="AppContext não foi inicializado no typer.Context",
    en="AppContext was not initialized in typer.Context",
)

@dataclass
class AppContext:
    settings: Settings
    changedir: Path
    width: int | None
    global_cache: bool
    update: bool
    offline: bool

    @staticmethod
    def load_from_context(ctx: typer.Context) -> AppContext:
        app_ctx: AppContext | None = ctx.obj
        if not isinstance(app_ctx, AppContext):
            logger.error(t(_APP_CONTEXT_NOT_SET))
            raise typer.Exit(1)
        return app_ctx