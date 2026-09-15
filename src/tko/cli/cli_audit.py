import tempfile
import time
from pathlib import Path

import typer

from tko.config.settings import Settings
from tko.cli.audit_preview import render_audit_preview, run_audit_preview, unpack_patch_history, unpack_audit_jsonl
from loguru import logger
from tko.i18n import Msg
from tko.util.console import Console
from tko.repository.audit_coordinator import AuditAlreadyRunning

app = typer.Typer(help="Audit repository activity", no_args_is_help=True)

@app.command("init", help="Start standalone audit watcher")
def audit_start(
    ctx: typer.Context,
    interval: int | None = typer.Option(None, "--interval", "-i", help="Snapshot interval in seconds"),
):
    from tko.cli.common import load_repo
    from tko.repository.repository_watcher import RepositoryWatcher

    settings: Settings = ctx.obj
    settings.rs.force_offline = True
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    if repo is None:
        return
    
    AUDIT_STARTING = Msg.parse(pt="Monitor de auditoria iniciado. Aperte Ctrl+C para finalizar.", 
                      en="Audit watcher started. Press Ctrl+C to stop.")
    if interval is None:
        interval = repo.audit.interval_seconds
        
    watcher = RepositoryWatcher(repo)
    try:
        watcher.start_watching(
            log_edits=False,
            log_audit=True,
            audit_verbose=True,
            audit_interval_seconds=interval,
            strict_audit=True,
        )
    except AuditAlreadyRunning as error:
        Console.print(str(error))
        raise typer.Exit(1) from error
    logger.info(f"{AUDIT_STARTING}")
    OPEN_TKO = Msg.parse(pt='Abra o tko em outro terminal para fazer as tarefas', en='Open tko in another terminal to perform tasks')
    Console.print(f"{OPEN_TKO}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        watcher.stop_watching()
        logger.info(f"{Msg.parse(pt='Monitor de auditoria parado.', en='Audit watcher stopped.')}")


@app.command("preview", help="Preview audit snapshots with fzf")
def audit_preview(
    ctx: typer.Context,
    target_list: list[Path] | None = typer.Argument(
        None,
        help="Files or directories to preview. Defaults to the repository audit folder.",
    ),
    index_file: Path | None = typer.Option(None, "--index-file", hidden=True),
    preview_index: int | None = typer.Option(None, "--preview-index", hidden=True),
    mode: str = typer.Option("diff", "--mode", hidden=True),
) -> None:
    if preview_index is not None:
        if index_file is None:
            raise typer.BadParameter("--index-file is required with --preview-index")
        render_audit_preview(index_file, preview_index, mode)
        return

    settings: Settings = ctx.obj

    if not target_list:
        target_list = [settings.rs.changedir]

    code = run_audit_preview(target_list)
    if code not in (0, 130):
        raise typer.Exit(code=code)


@app.command("unpack", help="Unpack audit data from a .json or .jsonl file into individual files")
def audit_unpack(
    source_file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
) -> None:
    output_dir = Path(tempfile.mkdtemp(prefix="tko-audit-unpack-"))

    if source_file.suffix == ".json":
        count, _ = unpack_patch_history(0, source_file, output_dir)
    elif source_file.suffix == ".jsonl":
        count, _ = unpack_audit_jsonl(0, source_file, output_dir)
    else:
        raise typer.BadParameter("Expected a .json or .jsonl file")

    Console.print(str(output_dir))
    logger.info(f"Unpacked {count} files to {output_dir}")


if __name__ == "__main__":
    app()
