from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

import typer
from tko.config.settings import Settings

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
            print("Error: App context is not properly set.")
            raise typer.Exit(1)
        return app_ctx