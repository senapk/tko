from __future__ import annotations

import re
import shutil
from pathlib import Path

import typer

from tko.feno.indexer import fix_readme
from tko.game.task_matcher import TaskMatcher
from tko.repository.git_cache import GitCache, UpdateMode
from tko.util.git_hub_url import GitHubUrl
from tko.config.user_data import UserData


app = typer.Typer(help="Build and materialize activity indexes")
_SOURCE_RE = re.compile(r"<!--\s*source:\s*(https?://[^\s]+)\s*-->")
_LINK_RE = re.compile(r"\((https?://[^)]+)\)")


def _task_key(line: str) -> str | None:
    match = re.search(r"`[^`]*@([^\s`]+)", line)
    return match.group(1) if match else None


def _external_reference(line: str, update: bool) -> str | None:
    if update:
        match = _SOURCE_RE.search(line)
        return match.group(1) if match else None
    match = _LINK_RE.search(line)
    return match.group(1) if match else None


def _materialize(index: Path, keys: list[str], update: bool) -> int:
    content = index.read_text(encoding="utf-8").splitlines()
    cache = GitCache(UserData.global_cache_dir(), update_mode=UpdateMode.ALWAYS if update else UpdateMode.IF_OLDER)
    selected = {key.removeprefix("@") for key in keys}
    for key in selected:
        TaskMatcher.validate_key(key)
    changed = 0
    output: list[str] = []

    for line in content:
        url = _external_reference(line, update)
        key = _task_key(line)
        if url is None:
            output.append(line)
            continue
        if key is None:
            raise typer.BadParameter("External activities require an explicit @key")
        TaskMatcher.validate_key(key)
        if selected and key not in selected:
            output.append(line)
            continue
        github = GitHubUrl.parse(url)
        if github is None or github.relative_path is None:
            raise typer.BadParameter(f"External activity must point to a GitHub README.md: {url}")
        origin, found = cache.git_hub_url_to_path(github, load_git=True)
        if not found:
            raise typer.BadParameter(f"Unable to download {url}")
        destination = index.parent / key
        if update and destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(origin.parent, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", ".cache", ".tko"))
        relative_readme = (destination / "README.md").relative_to(index.parent).as_posix()
        local_line = line.replace(f"({url})", f"({relative_readme})")
        if not _SOURCE_RE.search(local_line):
            local_line += f" <!-- source: {url} -->"
        output.append(local_line)
        changed += 1

    if changed:
        index.write_text("\n".join(output) + "\n", encoding="utf-8")
    return changed


@app.command("build", help="Validate and update a local activity index")
def index_build(
    index: Path = typer.Argument(...),
    base: Path = typer.Argument(...),
    yes: bool = typer.Option(False, "--yes", "-y"),
):
    fix_readme(index=index, base_dir=base, verbose=True, yes=yes)


@app.command("download", help="Materialize external activities")
def index_download(
    index: Path = typer.Argument(...),
    keys: list[str] = typer.Argument([]),
):
    _materialize(index, keys, update=False)


@app.command("update", help="Replace materialized external activities")
def index_update(
    index: Path = typer.Argument(...),
    keys: list[str] = typer.Argument([]),
):
    _materialize(index, keys, update=True)
