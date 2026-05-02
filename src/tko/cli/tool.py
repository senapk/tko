import typer
from pathlib import Path
from typing import Optional

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


@app.command("redirect", help="Create redirected markdown file")
def tool_redirect(
    target: str = typer.Argument(..., help="Directories"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file")
):
    from tko.feno.remote_md import Absolute
    Absolute.convert_or_copy_or_print(Path(target), output if output is None else Path(output))


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