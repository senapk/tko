from pathlib import Path

import typer

from tko.config.settings import Settings

app = typer.Typer(help="Manage class tasks")
# collect_app = typer.Typer(help="Collect data from many repositories")
# app.add_typer(collect_app, name="collect")

@app.command("tasks", help="Collect tasks report from many repositories")
def collect_tasks(
    ctx: typer.Context,
    path: list[str] = typer.Argument(..., help="Paths to repos"),
    csv: str = typer.Option(..., "--csv", help="Output CSV file"),
):
    from tko.collect.collect_many import CollectMany

    settings: Settings = ctx.obj
    repos = [Path(p) for p in path]

    CollectMany.load_tasks(settings.rs, repos, tasks_path=csv)

@app.command("skills", help="Collect skills report from many repositories")
def collect_skills(
    ctx: typer.Context,
    path: list[str] = typer.Argument(..., help="Paths to repos"),
    csv: str = typer.Option(..., "--csv", help="Output CSV file"),
    remote: str = typer.Option(..., "--remote", "-r", help="Remote target to load quests"),
    language: str = typer.Option(..., "--lang", "-l", help="Programming language for skills"),
):
    from tko.collect.collect_many import CollectMany

    settings: Settings = ctx.obj
    repos = [Path(p) for p in path]
    CollectMany.load_skills(rs=settings.rs, git_dir_list=repos, skills_path=csv, remote_index=remote, prog_lang=language)

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
