import re
import tempfile
import time
from pathlib import Path

import typer

from tko.config.settings import Settings
from tko.logger.patch_history import PatchHistory
from tko.logger.versions_writer import VersionsWriter
from loguru import logger
from tko.i18n import Msg
from tko.util.console import Console

app = typer.Typer(help="Audit repository activity", no_args_is_help=True)

_AUDIT_PERSISTENT_ENABLED = Msg(
    pt="Auditoria persistente habilitada",
    en="Persistent audit enabled",
)
_AUDIT_PERSISTENT_DISABLED = Msg(
    pt="Auditoria persistente desabilitada",
    en="Persistent audit disabled",
)
_AUDIT_PERSISTENT_STATUS = Msg(
    pt="Auditoria persistente: {status}",
    en="Persistent audit: {status}",
)


def _sanitize_filename(text: str) -> str:
    text = text.replace("/", "-").replace(":", "-").replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", text)


def _unpack_patch_history(json_file: Path, output_dir: Path) -> int:
    patches = PatchHistory().set_json_file(json_file).load_json().restore_all()
    stem = _sanitize_filename(json_file.stem)
    for index, patch in enumerate(patches, start=1):
        label = _sanitize_filename(patch.label)
        output_file = output_dir / f"{index:04d}_{label}_{stem}"
        output_file.write_text(patch.content, encoding="utf-8")
    return len(patches)


def _unpack_audit_jsonl(jsonl_file: Path, output_dir: Path) -> int:
    stem = _sanitize_filename(jsonl_file.stem)
    snapshots = VersionsWriter().load_history(jsonl_file).snapshots

    for index, snapshot in enumerate(snapshots, start=1):
        label = _sanitize_filename(snapshot.timestamp.strftime("%Y-%m-%d_%H-%M-%S"))
        output_file = output_dir / f"{index:04d}_{label}_{stem}"
        output_file.write_text(snapshot.content, encoding="utf-8")

    return len(snapshots)


@app.command("set", help="Enable or disable persistent audit in the repository")
def audit_set(
    ctx: typer.Context,
    on: bool = typer.Option(False, "--on", help="Enable persistent audit"),
    off: bool = typer.Option(False, "--off", help="Disable persistent audit"),
    interval: int | None = typer.Option(None, "--interval", "-i", help="Persistent audit interval in seconds"),
) -> None:
    from tko.cli.common import load_repo
    from tko.repository.repository_config import RepositoryConfig

    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs, show_warnings=True, auto_load=True)
    if repo is None:
        return

    if on and off:
        raise typer.BadParameter("Use only one of --on or --off")

    if not on and not off:
        status = "ON" if repo.audit.enabled else "OFF"
        interval_text = repo.audit.interval_seconds if repo.audit.interval_seconds is not None else "default"
        Console.print(f"{_AUDIT_PERSISTENT_STATUS}".format(status=f"{status} ({interval_text}s)"))
        return

    repo.audit.enabled = on
    if interval is not None:
        repo.audit.interval_seconds = interval
    RepositoryConfig(repo).save()
    Console.print(_AUDIT_PERSISTENT_ENABLED if on else _AUDIT_PERSISTENT_DISABLED)


@app.command("init", help="Initialize audit watcher")
def audit_init(
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
    
    AUDIT_STARTING = Msg(pt="Monitor de auditoria iniciado. Aperte Ctrl+C para finalizar.", 
                      en="Audit watcher started. Press Ctrl+C to stop.")

    watcher = RepositoryWatcher(repo)
    watcher.start_watching(log_edits=False, log_audit=True, audit_verbose=True, audit_interval_seconds=interval)
    logger.info(f"{AUDIT_STARTING}")
    OPEN_TKO = Msg(pt='Abra o tko em outro terminal para fazer as tarefas', en='Open tko in another terminal to perform tasks')
    Console.print(f"{OPEN_TKO}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        watcher.stop_watching()
        logger.info(f"{Msg(pt='Monitor de auditoria parado.', en='Audit watcher stopped.')}")


@app.command("unpack", help="Unpack audit data from a .json or .jsonl file into individual files")
def audit_unpack(
    source_file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
) -> None:
    output_dir = Path(tempfile.mkdtemp(prefix="tko-audit-unpack-"))

    if source_file.suffix == ".json":
        count = _unpack_patch_history(source_file, output_dir)
    elif source_file.suffix == ".jsonl":
        count = _unpack_audit_jsonl(source_file, output_dir)
    else:
        raise typer.BadParameter("Expected a .json or .jsonl file")

    Console.print(str(output_dir))
    logger.info(f"Unpacked {count} files to {output_dir}")


if __name__ == "__main__":
    app()
