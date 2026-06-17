import os
import re
import shlex
import subprocess
import sys
import tempfile
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from shutil import which


def _sanitize_filename(text: str) -> str:
    text = text.replace("/", "-").replace(":", "-").replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", text)


def _materialize_audit_history(jsonl_file: Path, output_dir: Path) -> list[Path]:
    from tko.logger.versions_writer import VersionsWriter

    stem = _sanitize_filename(f"{jsonl_file.parent.name}_{jsonl_file.stem}")
    history_dir = output_dir / stem
    history_dir.mkdir(parents=True, exist_ok=True)
    snapshots = VersionsWriter().load_history(jsonl_file).snapshots
    files: list[Path] = []

    for index, snapshot in enumerate(snapshots, start=1):
        label = _sanitize_filename(snapshot.timestamp.strftime("%Y-%m-%d_%H-%M-%S"))
        output_file = history_dir / f"{index:04d}_{label}_{stem}"
        output_file.write_text(snapshot.content, encoding="utf-8")
        files.append(output_file)

    return files


def _collect_preview_files(source_paths: list[Path], output_dir: Path) -> list[Path]:
    files: list[Path] = []
    for source_path in source_paths:
        if source_path.is_dir():
            audit_files = sorted(source_path.rglob("*.jsonl"))
            if audit_files:
                for audit_file in audit_files:
                    files.extend(_materialize_audit_history(audit_file, output_dir))
            else:
                files.extend(path for path in source_path.rglob("*") if path.is_file())
        elif source_path.is_file() and source_path.suffix == ".jsonl":
            files.extend(_materialize_audit_history(source_path, output_dir))
        elif source_path.is_file():
            files.append(source_path)

    return sorted(files)


def _build_preview_index(source_paths: list[Path], index_file: Path, output_dir: Path) -> list[Path]:
    files = _collect_preview_files(source_paths, output_dir)
    index_file.write_text("\n".join(str(path) for path in files), encoding="utf-8")
    return files


def _load_preview_index(index_file: Path) -> list[Path]:
    return [
        Path(line)
        for line in index_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _preview_command(index_file: Path, mode: str) -> str:
    base_args = [
        sys.executable,
        "-m",
        "tko.cli.audit_preview",
        "--index-file",
        str(index_file),
    ]
    return f"{shlex.join(base_args)} --preview-index {{1}} --mode {shlex.quote(mode)}"


def _context_args(mode: str) -> list[str]:
    if mode == "wide":
        return ["-U40"]
    if mode == "full":
        return ["-U999999", "--inter-hunk-context=999999"]
    return ["-U10"]


def _snapshot_timestamp(path: Path) -> datetime | None:
    name = re.sub(r"^[0-9]+_", "", path.name)
    match = re.search(
        r"([0-9]{4})-([0-9]{2})-([0-9]{2})[_-]([0-9]{2})-([0-9]{2})-([0-9]{2})",
        name,
    )
    if match is None:
        return None

    return datetime(
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        int(match.group(4)),
        int(match.group(5)),
        int(match.group(6)),
    )


def _format_elapsed(current: Path, previous: Path | None) -> str:
    if previous is None:
        return "--:--:--"

    current_ts = _snapshot_timestamp(current)
    previous_ts = _snapshot_timestamp(previous)
    if current_ts is None or previous_ts is None:
        return "--:--:--"

    total_seconds = int(abs((current_ts - previous_ts).total_seconds()))
    days, remaining = divmod(total_seconds, 86400)
    hours, remaining = divmod(remaining, 3600)
    minutes, seconds = divmod(remaining, 60)
    if days:
        return f"{days}d {hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _run_captured(args: list[str], input_text: str | None = None) -> str:
    result = subprocess.run(
        args,
        input=input_text,
        text=True,
        capture_output=True,
    )
    return result.stdout or result.stderr


def _write(text: str) -> None:
    sys.stdout.write(text)
    if not text.endswith("\n"):
        sys.stdout.write("\n")


def _render_file(path: Path, preview_cols: int) -> str:
    if which("bat") is not None:
        output = _run_captured(
            [
                "bat",
                "--color=always",
                "--tabs=4",
                f"--terminal-width={preview_cols}",
                str(path),
            ]
        )
        return "\n".join(output.splitlines()[3:])

    return path.read_text(encoding="utf-8", errors="replace")


def _render_diff(previous: Path, current: Path, mode: str, preview_cols: int) -> str:
    diff_output = _run_captured(
        [
            "git",
            "diff",
            "--no-index",
            *_context_args(mode),
            str(previous),
            str(current),
        ]
    )

    if which("delta") is not None:
        delta_output = _run_captured(
            [
                "delta",
                "--paging=never",
                "--side-by-side",
                "--line-numbers",
                "--true-color=always",
                "--tabs=4",
                f"--width={preview_cols}",
            ],
            input_text=diff_output,
        )
        return "\n".join(delta_output.splitlines()[5:])

    return diff_output


def render_audit_preview(index_file: Path, preview_index: int, mode: str) -> None:
    files = _load_preview_index(index_file)
    if preview_index < 1 or preview_index > len(files):
        _write("Indice invalido")
        return

    current = files[preview_index - 1]
    previous = files[preview_index - 2] if preview_index > 1 else None
    preview_cols = int(os.environ.get("FZF_PREVIEW_COLUMNS", "120"))
    yellow = "\033[33m"
    green = "\033[32m"
    blue = "\033[34m"
    reset = "\033[0m"
    shortcuts = "Alt+[1:diff | 2:wide | 3:full], Left:Previous, Right:Next"
    elapsed = _format_elapsed(current, previous)

    _write(
        f"{yellow}Elapsed={green}{elapsed}{yellow} | Mode={green}{mode}"
        f"{yellow} | Shortcuts={green}{shortcuts}{reset}"
    )
    if previous is None:
        _write(f"{blue}{current}{reset}")
    else:
        _write(f"{blue}{previous} {green} -> {blue}{current}{reset}")
    _write(f"{blue}{'-' * preview_cols}{reset}")

    if previous is None:
        _write("\n")
        _write(_render_file(current, preview_cols))
    else:
        _write(_render_diff(previous, current, mode, preview_cols))


def _run_audit_fzf(files: list[Path], index_file: Path) -> int:
    if which("fzf") is None:
        sys.stderr.write("fzf not found\n")
        return 1

    lines = [f"{index}\t{path}" for index, path in enumerate(files, start=1)]
    args = [
        "fzf",
        "--height=100%",
        "--layout=reverse",
        "--border=none",
        "--list-border=sharp",
        "--ansi",
        "--info=inline",
        "--delimiter=\t",
        "--with-nth=2..",
        "--preview",
        _preview_command(index_file, "diff"),
        "--preview-window=down:80%:noborder",
        "--bind",
        "left:up,right:down",
        "--bind",
        "up:preview-up,down:preview-down",
        "--bind",
        "pgup:preview-page-up,pgdn:preview-page-down",
        "--bind",
        f"alt-1:change-preview({_preview_command(index_file, 'diff')})",
        "--bind",
        f"alt-2:change-preview({_preview_command(index_file, 'wide')})",
        "--bind",
        f"alt-3:change-preview({_preview_command(index_file, 'full')})",
    ]
    return subprocess.run(args, input="\n".join(lines), text=True).returncode


def run_audit_preview(source_paths: list[Path]) -> int:
    with tempfile.TemporaryDirectory(prefix="tko-audit-preview-") as tmp:
        tmp_dir = Path(tmp)
        index_file = tmp_dir / "index"
        files = _build_preview_index(source_paths, index_file, tmp_dir)
        if not files:
            sys.stderr.write("Nenhum arquivo encontrado\n")
            return 1

        return _run_audit_fzf(files, index_file)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--index-file", type=Path, required=True)
    parser.add_argument("--preview-index", type=int, required=True)
    parser.add_argument("--mode", default="diff")
    args = parser.parse_args()
    render_audit_preview(args.index_file, args.preview_index, args.mode)


if __name__ == "__main__":
    main()
