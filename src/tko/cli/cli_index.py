from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
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


@dataclass(frozen=True)
class _Materialization:
    line_index: int
    source_url: str
    destination: Path
    rendered_line: str


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


def _materialize(index: Path, paths: list[str], replace: bool) -> int:
    lines: list[str] = index.read_text(encoding="utf-8").splitlines()
    selected: set[str] = _selected_paths(paths)
    index_root: Path = index.parent.resolve()
    operations: list[_Materialization] = []
    destinations: set[Path] = set()

    for line_index, line in enumerate(lines):
        matcher = TaskMatcher()
        if not matcher.match_pattern(line):
            continue

        try:
            source_url: str | None = source_url_from_line(line)
            if matcher.is_url:
                url: str = matcher.link
                destination_path: Path = activity_path_from_source_url(url)
            elif source_url is not None:
                url = source_url
                destination_path = activity_path_from_local_link(matcher.link)
            else:
                continue
        except ValueError as exc:
            raise typer.BadParameter(str(exc)) from exc
        if selected and destination_path.as_posix() not in selected:
            continue

        destination: Path = index.parent / destination_path
        if not destination.resolve().is_relative_to(index_root) or destination.is_symlink():
            raise typer.BadParameter(f"Unsafe activity destination: {destination}")
        if destination in destinations:
            raise typer.BadParameter(f"Duplicate activity destination: {destination_path}")
        if destination.exists():
            if not destination.is_dir():
                raise typer.BadParameter(f"Activity destination is not a directory: {destination}")
            if not replace:
                if matcher.is_url:
                    raise typer.BadParameter(
                        f"Activity destination already exists: {destination}. Use --replace to overwrite it."
                    )
                continue

        local_readme: str = (destination_path / "README.md").as_posix()
        local_line: str = _without_legacy_key(line, matcher).replace(
            f"({matcher.link})", f"({local_readme})"
        )
        operations.append(
            _Materialization(line_index, url, destination, replace_source_comment(local_line, url))
        )
        destinations.add(destination)

    cache = GitCache(
        UserData.global_cache_dir(),
        update_mode=UpdateMode.ALWAYS if replace else UpdateMode.IF_OLDER,
    )
    for operation in operations:
        github: GitHubUrl | None = GitHubUrl.parse(operation.source_url)
        assert github is not None  # validated by activity-path and source-comment parsing
        origin, found = cache.git_hub_url_to_path(github, load_git=True)
        if not found:
            raise typer.BadParameter(f"Unable to download {operation.source_url}")
        if operation.destination.exists():
            if not replace:
                raise typer.BadParameter(f"Activity destination already exists: {operation.destination}")
            shutil.rmtree(operation.destination)
        operation.destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            origin.parent,
            operation.destination,
            ignore=shutil.ignore_patterns(".git", ".cache", ".tko"),
        )
        lines[operation.line_index] = operation.rendered_line

    if operations:
        index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(operations)


def index_sync(
    index: Path = typer.Argument(...),
    from_sources: list[Path] = typer.Option(..., "--from", help="Task source directory; repeat for multiple sources"),
    save: bool = typer.Option(False, "--save", help="Copy index titles into task READMEs"),
    load: bool = typer.Option(False, "--load", help="Load task README titles into the index"),
    yes: bool = typer.Option(False, "--yes", "-y"),
    no_align: bool = typer.Option(False, "--no-align", help="Do not align task keys and fields"),
) -> None:
    source_dirs: list[Path] = [path if path.is_absolute() else index.parent / path for path in from_sources]
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


def index_pull(
    index: Path = typer.Argument(...),
    paths: list[str] = typer.Argument([], help="Activity paths, such as labs/fila"),
    replace: bool = typer.Option(False, "--replace", help="Replace existing local copies and discard local changes"),
) -> None:
    _materialize(index, paths, replace=replace)
