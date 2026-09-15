"""Plan moves of activity trees together with the persisted task references."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
import stat

from tko.repository.task_migration_transaction import (
    DirectoryChange, FileChange, MigrationPlan, safe_path, tree_entries,
)


def activity_relative(root: Path, path: Path) -> str:
    relative: str = path.relative_to(root).as_posix()
    if relative == "." or any(part in {".git", ".tko", ".."} for part in Path(relative).parts):
        raise ValueError(f"Unsafe activity path: {path}")
    _ = safe_path(root, relative)
    return relative


def plan_activity_moves(
    plan: MigrationPlan,
    keys: set[str],
    canonical_paths: Mapping[str, Path],
    source_roots: Mapping[str, Path],
    resolve: Callable[[str], str],
) -> None:
    proposals: dict[str, set[str]] = {}
    for key in sorted(keys):
        source, separator, old_path = key.partition("@")
        if not separator or not old_path or key in canonical_paths:
            continue
        origins: set[Path] = {plan.root / source / old_path}
        if source in source_roots:
            origins.add(source_roots[source] / old_path)
        for origin in sorted(origins):
            old: str = activity_relative(plan.root, origin)
            if not origin.exists():
                continue
            destination_key: str = resolve(key)
            if destination_key == key:
                continue
            new_source, _, new_path = destination_key.partition("@")
            destination: Path = canonical_paths.get(destination_key, plan.root / new_source / new_path)
            new: str = activity_relative(plan.root, destination)
            if old == new:
                continue
            if any(path.is_relative_to(origin) for path in plan.inputs) or any(
                path.is_relative_to(origin) for path in canonical_paths.values()
            ):
                continue
            proposals.setdefault(old, set()).add(new)
    moves: dict[str, str] = {}
    for old, destinations in proposals.items():
        if len(destinations) != 1:
            plan.errors.append(f"Ambiguous activity destination: {old}")
        else:
            moves[old] = next(iter(destinations))
    for old in moves:
        for new in moves.values():
            if Path(new).is_relative_to(old) or Path(old).is_relative_to(new):
                plan.errors.append(f"Overlapping activity source and destination: {old} -> {new}")
    if plan.errors or not moves:
        return
    plan.moves = moves
    nodes: set[str] = set()
    for relative in sorted(moves.keys() | set(moves.values())):
        entries: set[str] = tree_entries(plan.root, relative)
        plan.trees[relative] = entries
        nodes.update(entries)

    def destination_for(relative: str) -> str:
        parents: list[str] = [old for old in moves if Path(relative).is_relative_to(old)]
        if not parents:
            return relative
        old: str = max(parents, key=lambda value: len(Path(value).parts))
        return (Path(moves[old]) / Path(relative).relative_to(old)).as_posix()

    originals: dict[str, tuple[bytes, int, int]] = {}
    desired: dict[str, tuple[bytes, int, int]] = {}
    before_dirs: dict[str, int] = {}
    after_dirs: dict[str, int] = {}
    # Existing destination files keep their metadata when identical files merge.
    ordered: list[str] = sorted(nodes, key=lambda value: (destination_for(value.rstrip("/")) != value.rstrip("/"), value))
    for node in ordered:
        relative = node.rstrip("/")
        path: Path = safe_path(plan.root, relative)
        target: str = destination_for(relative)
        mode: int = stat.S_IMODE(path.stat().st_mode)
        if node.endswith("/"):
            before_dirs[relative] = mode
            after_dirs.setdefault(target, mode)
            continue
        metadata: tuple[bytes, int, int] = (path.read_bytes(), mode, path.stat().st_mtime_ns)
        originals[relative] = metadata
        plan.inputs[path] = metadata[0]
        if target in desired and desired[target][:2] != metadata[:2]:
            plan.errors.append(f"Conflicting activity files at {target}; no files will be overwritten")
        else:
            desired.setdefault(target, metadata)
    for relative in list(after_dirs):
        for parent in Path(relative).parents:
            if parent == Path("."):
                break
            path = safe_path(plan.root, parent.as_posix())
            if path.exists():
                if not path.is_dir():
                    plan.errors.append(f"Activity destination parent is not a directory: {parent}")
                break
            after_dirs.setdefault(parent.as_posix(), 0o755)
    if desired.keys() & after_dirs.keys():
        plan.errors.append("Activity destinations contain file/directory collisions")
    for relative in sorted(before_dirs.keys() | after_dirs.keys()):
        before: int | None = before_dirs.get(relative)
        path = safe_path(plan.root, relative)
        if before is None and path.exists():
            if not path.is_dir():
                plan.errors.append(f"Activity directory collides with a file: {relative}")
                continue
            before = stat.S_IMODE(path.stat().st_mode)
        after: int | None = after_dirs.get(relative)
        if before != after:
            plan.directories.append(DirectoryChange(relative, before, after))
    for relative in sorted(originals.keys() | desired.keys()):
        old_file: tuple[bytes, int, int] | None = originals.get(relative)
        new_file: tuple[bytes, int, int] | None = desired.get(relative)
        if old_file != new_file:
            plan.changes.append(FileChange(
                relative, None if old_file is None else old_file[0], None if new_file is None else new_file[0],
                None if old_file is None else old_file[1], None if new_file is None else new_file[1],
                None if old_file is None else old_file[2], None if new_file is None else new_file[2],
            ))
