import typer
from pathlib import Path

app = typer.Typer(help="Manage class tasks")

@app.command("collect", help="Colect and merge data from many repos")
def class_collect(
    path: list[str] = typer.Argument(..., help="Paths to repos"),
    json: str | None = typer.Option(None, "--json", "-j", help="Path to save the extracted JSON data"),
    csv: str | None = typer.Option(None, "--csv", "-c", help="Path to save the extracted CSV data"),
    block_prefix: str | None = typer.Option(None, "--block_prefix", "-b", help="Block prefix to insert in csv file")
):
    from tko.collect.collect_many import CollectMany
    git_repo_list = [Path(x) for x in path]
    CollectMany.execute(git_repo_list, json_path=json, csv_path=csv, block_prefix=block_prefix)

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
