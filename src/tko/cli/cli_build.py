"""Commands that build task and index artifacts."""

import typer

from tko.cli.cli_index import index_pull, index_sync
from tko.cli.cli_task import task_build

app: typer.Typer = typer.Typer(help="Build task and index artifacts", no_args_is_help=True)
app.command("task", help="Build task artifacts")(task_build)
app.command("index", help="Sync an activity index with local source directories")(index_sync)
app.command("download", help="Download external activities from an index")(index_pull)
