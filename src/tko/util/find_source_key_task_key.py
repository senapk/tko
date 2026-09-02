from pathlib import Path


def find_source_key_task_key(sources_dir_map: dict[Path, str], path: Path) -> str | None:
    for source_dir, source_name in sources_dir_map.items():
        try:
            resolved_source = source_dir.resolve()
            current = path.resolve() if path.resolve().is_dir() else path.resolve().parent
            while current != resolved_source and current.is_relative_to(resolved_source):
                if (current / "README.md").is_file():
                    relative = current.relative_to(resolved_source).as_posix()
                    return f"{source_name}@{relative}"
                current = current.parent
            return None
        except ValueError:
            continue
    return None
