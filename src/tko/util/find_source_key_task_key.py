from pathlib import Path


def find_source_key_task_key(sources_dir_map: dict[Path, str], path: Path) -> str | None:
    for source_dir, source_name in sources_dir_map.items():
        try:
            relative_path = path.resolve().relative_to(source_dir.resolve())
            first_parent = relative_path.parts[0] if relative_path.parts else ""
            if not (source_dir/first_parent/"README.md").exists():
                return None
            return f"{source_name}@{first_parent}"
        except ValueError:
            continue
    return None