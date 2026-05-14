import typer
from pathlib import Path
from typing import Optional


def _build_readme_candidates_from_repo_url(repo_url: str) -> list[str]:
    # Normalizes common git URL forms to GitHub web URLs and returns branch candidates.
    normalized: str = repo_url.strip()
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    if normalized.startswith("git@github.com:"):
        normalized = "https://github.com/" + normalized[len("git@github.com:") :]
    normalized = normalized.rstrip("/")
    return [
        f"{normalized}/blob/main/README.md",
    ]

app = typer.Typer(help="Utility tools for one-off operations")

@app.command("mdpp", help="Preprocessor for markdown files")
def tool_mdpp(
    targets: Optional[list[str]] = typer.Argument(None, help="Readme files or None to default task behavior"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="quiet mode"),
    clean: bool = typer.Option(False, "--clean", "-c", help="clean mode")
):
    from tko.feno.mdpp import Action, Mdpp

    target_paths = [Path(x) for x in targets] if targets else [Path("README.md")]
    if not targets:
        print(f"Updating README.md in {Path().name}")

    action = Action.CLEAN if clean else Action.RUN
    for target in target_paths:
        Mdpp.update_file(target, action, quiet)


@app.command("older", help="Check if the source is newer than the target")
def tool_older(
    targets: list[str] = typer.Argument(..., help="Target files or directories")
):
    from tko.feno.older import Older
    print(Older.find_older([Path(x) for x in targets]))


@app.command("diff", help="Show diff for 2 inputs or files")
def tool_diff(
    target_a: str = typer.Argument(..., help="First target to be compared"),
    target_b: str = typer.Argument(..., help="Second target to be compared"),
    path: bool = typer.Option(False, "--path", "-f", help="Targets are paths"),
    text: bool = typer.Option(False, "--text", "-t", help="Compare two texts"),
    side: bool = typer.Option(False, "--side", "-s", help="Diff mode side-by-side"),
    down: bool = typer.Option(False, "--down", "-d", help="Diff mode up-to-down")
):
    from tko.cmds.cmd_diff import cmd_diff
    cmd_diff(target_a, target_b, side, path)


@app.command("rebase-links", help="Rebase markdown links to work from a new path")
def tool_rebase_links(
    ctx: typer.Context,
    target: str = typer.Argument(..., help="URL or local path to the source markdown"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output markdown file path (default: current directory with source filename)"),
):
    import os
    import tempfile
    from urllib.parse import urlparse
    from tko.util.decoder import Decoder
    from tko.util.github_url import GitHubUrl
    from tko.feno.link_rebase import LinkRebase
    from tko.app_context import AppContext

    # Determine output filename and path
    if output is None:
        if target.startswith("@"):
            filename: str = "README.md"
        elif target.startswith("https://"):
            parsed_url = urlparse(target)
            filename = Path(parsed_url.path).name or "README.md"
        else:
            filename = Path(target).name
        output_path: Path = Path(filename)
    else:
        output_path = Path(output)

    if target.startswith("@"):
        alias: str = target[1:]
        app_ctx: AppContext = AppContext.load_from_context(ctx)
        settings = app_ctx.settings
        repo_url: str = settings.get_alias_git(alias)
        candidates: list[str] = _build_readme_candidates_from_repo_url(repo_url)

        last_error: Exception | None = None
        for candidate in candidates:
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    temp_file: str = str(Path(tmpdir) / "temp.md")
                    remote: GitHubUrl = GitHubUrl(candidate)
                    remote.download_and_rebase(temp_file)
                    print(f"Arquivo url={candidate} baixado com sucesso")
                    print("Rebase concluído")
                    print(f"Arquivo salvo no path: {output_path}")
                    # Copy from temp to final output
                    import shutil
                    shutil.copy(temp_file, output_path)
                return
            except Exception as exc:
                last_error = exc

        raise Warning(f"Não foi possível baixar README.md para @{alias}: {last_error}")

    if target.startswith("https://"):
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file: str = str(Path(tmpdir) / "temp.md")
            remote: GitHubUrl = GitHubUrl(target)
            remote.download_and_rebase(temp_file)
            print(f"Arquivo url={target} baixado com sucesso")
            print("Rebase concluído")
            print(f"Arquivo salvo no path: {output_path}")
            # Copy from temp to final output
            import shutil
            shutil.copy(temp_file, output_path)
    else:
        source_path: Path = Path(target)
        relative_folder: Path = Path(os.path.relpath(source_path.parent, output_path.parent))
        content: str = Decoder.load(source_path)
        content = LinkRebase.change_to_relative_folder(content, relative_folder)
        Decoder.save(output_path, content)
        print("Rebase concluído")
        print(f"Arquivo salvo no path: {output_path}")


@app.command("filter", help="Filter code removing answers")
def tool_filter(
    target: str = typer.Argument(..., help="file or directory to process"),
    update: bool = typer.Option(False, "--update", "-u", help="update source file"),
    cheat: bool = typer.Option(False, "--cheat", "-c", help="recursive cheat mode cleaning comments on students files"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="output target"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="recursive mode"),
    force: bool = typer.Option(False, "--force", "-f", help="force mode"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="quiet mode"),
    indent: int = typer.Option(0, "--indent", "-i", help="indent using spaces")
):
    from tko.feno.filter import CodeFilter

    is_recursive = recursive or cheat

    if is_recursive:
        CodeFilter.cf_recursive(target, output if output is None else Path(output), force=force, cheat=cheat, quiet=quiet, indent=indent)
        raise typer.Exit()

    CodeFilter.cf_single_file(Path(target), None if output is None else Path(output), update, cheat)


@app.command("html", help="Generate HTML file from markdown file")
def tool_html(
    input_file: str = typer.Argument(..., help="Input markdown file"),
    output_file: str = typer.Argument(..., help="Output HTML file"),
    title: str = typer.Option("Problema", "--title", help="Title of the HTML file")
):
    from tko.feno.title import FenoTitle
    from tko.feno.html import convert_markdown_to_html

    if not input_file.endswith('.md'):
        print("Erro: O arquivo de entrada Markdown deve ter a extensão .md")
        raise typer.Exit(1)
    if not output_file.endswith('.html'):
        print("Erro: O arquivo de saída HTML deve ter a extensão .html")
        raise typer.Exit(1)

    final_title = title if title != "Problema" else FenoTitle.extract_title(Path(input_file))
    convert_markdown_to_html(final_title, Path(input_file), Path(output_file))


if __name__ == "__main__":
    app()