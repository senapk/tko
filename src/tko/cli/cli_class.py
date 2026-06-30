import typer
from pathlib import Path

from tko.config.settings import Settings

app = typer.Typer(help="Manage class tasks")

@app.command("collect", help="Colect and merge data from many repos")
def class_collect(
    ctx: typer.Context,
    path: list[str] = typer.Argument(..., help="Paths to repos"),
    tasks: str | None = typer.Option(None, "--tasks", "-t", help="Path to save the extracted tasks CSV data"),
    skills: str | None = typer.Option(None, "--skills", "-s", help="Path to save the extracted skills CSV data"),
):
    from tko.collect.collect_many import CollectMany
    git_repo_list = [Path(x) for x in path]
    settings: Settings = ctx.obj
    CollectMany.execute(settings.rs, git_repo_list, tasks_path=tasks, skills_path=skills)

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
