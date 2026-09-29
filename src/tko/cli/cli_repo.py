from pathlib import Path
import sys
import subprocess

import typer

from tko.config.settings import Settings
from tko.cli.common import load_repo
from tko.cli.cli_profile import app as profile_app
from tko.cli.cli_source import app as source_app
from tko.cli.cli_config_audit import app as audit_app

app = typer.Typer(help="Manage the current TKO repository", no_args_is_help=True)
app.add_typer(profile_app, name="profile")
app.add_typer(source_app, name="source")
app.add_typer(audit_app, name="audit")


@app.command("init", help="Initialize an empty TKO repository")
def repo_init(
    ctx: typer.Context,
    language: str | None = typer.Option(None, "--language", "-l"),
    skip: bool = typer.Option(False, "--skip-sources", "-s"),
    profile: str | None = typer.Option(None, "--profile"),
) -> None:
    from tko.repository.repository_starter import RepositoryStarter

    settings: Settings = ctx.obj
    RepositoryStarter(settings, language=language, skip_add_remote=skip, profile_uri=profile).execute()


@app.command("list", help="List tasks available in repository sources")
def repo_list(
    ctx: typer.Context,
    all: bool = typer.Option(False, "--all", "-a"),
    downloaded: bool = typer.Option(False, "--downloaded"),
    quests: bool = typer.Option(False, "--quest", "-q"),
) -> None:
    from tko.cmds.cmd_open import CmdOpen

    settings: Settings = ctx.obj
    repo, _ = load_repo(settings.rs)
    if repo is None:
        raise typer.Exit(1)
    CmdOpen(settings, repo).list(show_all=all, only_down=downloaded, show_quests=quests)


@app.command("migrate", help="Migrate persisted task identities offline")
def repo_migrate(
    workspace: Path = typer.Argument(Path(".")),
    dry_run: bool = typer.Option(False, "--dry-run"),
    mapping: Path | None = typer.Option(None, "--map"),
    recover: bool = typer.Option(False, "--recover"),
) -> None:
    from tko.repository.task_migration import TaskDataMigration, read_mapping
    from tko.repository.task_migration_transaction import MigrationPlan, recover_migration

    try:
        if recover:
            if dry_run or mapping is not None:
                raise ValueError("--recover cannot be combined with --dry-run or --map")
            typer.echo(f"Migração revertida. Backup: {recover_migration(workspace)}")
            return
        plan: MigrationPlan = TaskDataMigration(workspace, read_mapping(mapping)).inspect()
        for old, new in sorted(plan.mapping.items()):
            if old != new:
                typer.echo(f"{old} -> {new}")
        for old, new in sorted(plan.moves.items()):
            typer.echo(f"move directory: {old} -> {new}")
        for change in plan.changes:
            action: str = "delete" if change.after is None else "create" if change.before is None else "update"
            typer.echo(f"{action}: {change.relative}")
        if plan.errors:
            for error in plan.errors:
                typer.echo(error, err=True)
            raise typer.Exit(1)
        if dry_run:
            typer.echo(f"Simulação: {len(plan.changes)} arquivo(s). Execute sem --dry-run com o TKO fechado.")
            return
        already_migrated: bool = not plan.changes and not plan.directories
        plan.apply()
        typer.echo("Dados já migrados." if already_migrated else "Migração concluída.")
    except (ValueError, OSError) as exc:
        typer.echo(f"Migração falhou: {exc}", err=True)
        if (workspace / ".tko" / "migration-pending.json").exists():
            typer.echo("Aplicação interrompida. Execute o mesmo comando com --recover.", err=True)
        raise typer.Exit(1) from exc
