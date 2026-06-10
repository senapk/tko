import re
import tempfile
import time
from pathlib import Path

import typer

from tko.config.settings import Settings
from tko.logger.audit_tracker import AuditElement
from tko.logger.patch_history import PatchHistory
from loguru import logger
from tko.i18n import Msg, t
from tko.util.console import Console

app = typer.Typer(help="Audit repository activity", no_args_is_help=True)


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
    count = 0
    with jsonl_file.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            element = AuditElement.from_jsonl_line(line)
            label = _sanitize_filename(element.timestamp.strftime("%Y-%m-%d_%H-%M-%S"))
            output_file = output_dir / f"{index:04d}_{label}_{stem}"
            output_file.write_text(element.content, encoding="utf-8")
            count += 1
    return count


@app.command("init")
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
    
    watcher = RepositoryWatcher(repo)
    watcher.start_watching(log_edits=False, log_audit=True, audit_verbose=True, audit_interval_seconds=interval)
    logger.info(t(Msg(pt="Monitor de auditoria iniciado. Aperte Ctrl+C para finalizar.", 
                      en="Audit watcher started. Press Ctrl+C to stop.")))
    
    Console.print(t(Msg(pt="Abra o tko em outro terminal para fazer as tarefas", 
                        en="Open tko in another terminal to perform tasks")))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        watcher.stop_watching()
        logger.info(t(Msg(pt="Monitor de auditoria parado.", en="Audit watcher stopped.")))


@app.command("unpack")
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
