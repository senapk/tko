from pathlib import Path

import typer

from tko.config.settings import Settings

app = typer.Typer(help="Manage class tasks")
collect_app = typer.Typer(help="Collect data from many repositories")

app.add_typer(collect_app, name="collect")

@collect_app.command("tasks")
def collect_tasks(
    ctx: typer.Context,
    path: list[str] = typer.Argument(..., help="Paths to repos"),
    csv: str = typer.Option(None, "--csv", help="Output CSV file"),
):
    from tko.collect.collect_many import CollectMany

    settings: Settings = ctx.obj
    repos = [Path(p) for p in path]

    CollectMany.load_tasks(settings.rs, repos, tasks_path=csv)

@collect_app.command("skills")
def collect_skills(
    ctx: typer.Context,
    path: list[str] = typer.Argument(..., help="Paths to repos"),
    csv: str | None = typer.Option(None, "--csv", help="Output CSV file"),
    remote: str | None = typer.Option( None, "--remote", "-r", help="Remote target to load quests"),
):
    from tko.collect.collect_many import CollectMany

    settings: Settings = ctx.obj
    repos = [Path(p) for p in path]

    CollectMany.load_skills(settings.rs, repos, skills_path=csv, remote=remote)

@app.command("pull", help="Perform git pull in many repos using threads")
def class_pull(
    path: list[str] = typer.Argument(..., help="Paths to repos"),
    threads: int = typer.Option(10, "--threads", "-t", help="Number of threads")
):
    from tko.collect.pull import Pull
    path_list = [Path(p) for p in path]
    Pull.pull_all_parallel(path_list, threads)

if __name__ == "__main__":
    app()
