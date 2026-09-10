from __future__ import annotations

import re
import shutil
from pathlib import Path

import typer

from tko.feno.indexer import fix_readme
from tko.feno.task_source import (
    activity_path_from_local_link,
    activity_path_from_source_url,
    replace_source_comment,
    source_url_from_line,
)
from tko.game.task_matcher import TaskMatcher
from tko.repository.git_cache import GitCache, UpdateMode
from tko.util.git_hub_url import GitHubUrl
from tko.config.user_data import UserData


app = typer.Typer(help="Build and materialize activity indexes")


def _selected_paths(paths: list[str]) -> set[str]:
    selected: set[str] = set()
    for path in paths:
        try:
            selected.add(activity_path_from_local_link(f"{path.removeprefix('@').rstrip('/')}/README.md").as_posix())
        except ValueError as exc:
            raise typer.BadParameter(f"Invalid activity path: {path}") from exc
    return selected


def _without_legacy_key(line: str, matcher: TaskMatcher) -> str:
    if matcher.legacy_key_token is None:
        return line
    without_key = line.replace(matcher.legacy_key_token, "", 1)
    return re.sub(r"`\s+", "`", without_key, count=1)


def _materialize(index: Path, paths: list[str], update: bool) -> int:
    content = index.read_text(encoding="utf-8").splitlines()
    cache = GitCache(UserData.global_cache_dir(), update_mode=UpdateMode.ALWAYS if update else UpdateMode.IF_OLDER)
    selected = _selected_paths(paths)
    changed = 0
    output: list[str] = []

    for line in content:
        matcher = TaskMatcher()
        if not matcher.match_pattern(line):
            output.append(line)
            continue

        try:
            url = source_url_from_line(line) if update else (matcher.link if matcher.is_url else None)
            destination_path = (
                activity_path_from_local_link(matcher.link)
                if update and url is not None
                else activity_path_from_source_url(url) if url is not None else None
            )
        except ValueError as exc:
            raise typer.BadParameter(str(exc)) from exc
        if url is None:
            output.append(line)
            continue
        assert destination_path is not None
        if selected and destination_path.as_posix() not in selected:
            output.append(line)
            continue
        if update and matcher.is_url:
            raise typer.BadParameter("Materialized activities must keep a local README.md link before update")
        github = GitHubUrl.parse(url)
        assert github is not None  # guaranteed by activity-path validation
        origin, found = cache.git_hub_url_to_path(github, load_git=True)
        if not found:
            raise typer.BadParameter(f"Unable to download {url}")
        destination = index.parent / destination_path
        if update and destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(origin.parent, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", ".cache", ".tko"))
        relative_readme = (destination / "README.md").relative_to(index.parent).as_posix()
        local_line = _without_legacy_key(line, matcher).replace(f"({matcher.link})", f"({relative_readme})")
        local_line = replace_source_comment(local_line, url)
        output.append(local_line)
        changed += 1

    if changed:
        index.write_text("\n".join(output) + "\n", encoding="utf-8")
    return changed


@app.command("build", help="Validate and update a local activity index")
def index_build(
    index: Path = typer.Argument(...),
    from_sources: list[Path] = typer.Option(..., "--from", help="Task source directory; repeat for multiple sources"),
    save: bool = typer.Option(False, "--save", help="Copy index titles into task READMEs"),
    load: bool = typer.Option(False, "--load", help="Load task README titles into the index"),
    yes: bool = typer.Option(False, "--yes", "-y"),
    no_align: bool = typer.Option(False, "--no-align", help="Do not align task keys and fields"),
):
    source_dirs = [path if path.is_absolute() else index.parent / path for path in from_sources]
    for source_dir in source_dirs:
        if not source_dir.is_dir():
            raise typer.BadParameter(f"Source directory not found: {source_dir}", param_hint="--from")
    fix_readme(
        index=index,
        base_dirs=source_dirs,
        verbose=True,
        save_titles=save,
        load_titles=load,
        yes=yes,
        align=not no_align,
    )


@app.command("download", help="Materialize external activities")
def index_download(
    index: Path = typer.Argument(...),
    paths: list[str] = typer.Argument([], help="Activity paths, such as labs/fila"),
):
    _materialize(index, paths, update=False)


@app.command("update", help="Replace materialized external activities")
def index_update(
    index: Path = typer.Argument(...),
    paths: list[str] = typer.Argument([], help="Activity paths, such as labs/fila"),
):
    _materialize(index, paths, update=True)
