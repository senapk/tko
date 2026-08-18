import typer
from pathlib import Path
from typing import Optional
from tko.config.settings import Settings
from tko.i18n import Msg
from tko.util.console import Console


_CLI_TOOL_MDPP_UPDATING_README = Msg.parse(
    pt="Atualizando README.md em {folder}",
    en="Updating README.md in {folder}",
)
_CLI_TOOL_REBASE_URL_DOWNLOADED = Msg.parse(
    pt="Arquivo url={url} baixado com sucesso",
    en="File url={url} downloaded successfully",
)
_CLI_TOOL_REBASE_DONE = Msg.parse(
    pt="Rebase concluído",
    en="Rebase completed",
)
_CLI_TOOL_REBASE_SAVED_PATH = Msg.parse(
    pt="Arquivo salvo no path: {path}",
    en="File saved at path: {path}",
)
_CLI_TOOL_REBASE_ALIAS_README_FAILED = Msg.parse(
    pt="Não foi possível baixar README.md para @{alias}: {error}",
    en="Could not download README.md for @{alias}: {error}",
)
_CLI_TOOL_HTML_INPUT_MD_REQUIRED = Msg.parse(
    pt="Erro: O arquivo de entrada Markdown deve ter a extensão .md",
    en="Error: Input Markdown file must have the .md extension",
)
_CLI_TOOL_HTML_OUTPUT_HTML_REQUIRED = Msg.parse(
    pt="Erro: O arquivo de saída HTML deve ter a extensão .html",
    en="Error: Output HTML file must have the .html extension",
)


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
        Console.print(_CLI_TOOL_MDPP_UPDATING_README.t().format(folder=Path().name))

    action = Action.CLEAN if clean else Action.RUN
    for target in target_paths:
        Mdpp.update_file(target, action, quiet)


@app.command("older", help="Check if the source is newer than the target")
def tool_older(
    targets: list[str] = typer.Argument(..., help="Target files or directories")
):
    from tko.feno.older import Older
    Console.print(Older.find_older([Path(x) for x in targets]))


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


@app.command("rebase", help="Rebase markdown links to work from a new path")
def tool_rebase_links(
    ctx: typer.Context,
    target: str = typer.Argument(..., help="URL or local path to the source markdown"),
    output: str = typer.Option(..., "--output", "-o", help="Output markdown file path (default: current directory with source filename)"),
    relative: str | None = typer.Option(None, "--relative", "-s", help="If None, the rebase will be done relative to target"),
):
    import os
    import tempfile
    from tko.util.decoder import Decoder
    from tko.util.git_hub_url_downloader import GitHubUrlDownloader
    from tko.feno.link_rebase import LinkRebase

    # Determine output filename and path
    output_path = Path(output)

    if target.startswith("@"):
        alias: str = target[1:]
        settings: Settings = ctx.obj
        file_url: str | None = settings.get_alias_git(alias)
        if file_url is None:
            Console.print(_CLI_TOOL_REBASE_ALIAS_README_FAILED.t().format(alias=alias, error="Alias not found"))
            return
        target = file_url

    if target.startswith("https://"):
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file: str = str(Path(tmpdir) / "temp.md")
            ghu_downloader: GitHubUrlDownloader = GitHubUrlDownloader(target)
            ghu_downloader.download_and_rebase(temp_file)
            Console.print(_CLI_TOOL_REBASE_URL_DOWNLOADED.t().format(url=target))
            Console.print(_CLI_TOOL_REBASE_DONE)
            Console.print(_CLI_TOOL_REBASE_SAVED_PATH.t().format(path=output_path))
            # Copy from temp to final output
            import shutil
            shutil.copy(temp_file, output_path)
    else:
        source_path: Path = Path(target)
        relative_folder: Path = Path(os.path.relpath(source_path.parent, output_path.parent))
        content: str = Decoder.load(source_path)
        content = LinkRebase.change_to_relative_folder(content, relative_folder)
        Decoder.save(output_path, content)
        Console.print(_CLI_TOOL_REBASE_DONE)
        Console.print(_CLI_TOOL_REBASE_SAVED_PATH.t().format(path=output_path))


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
        Console.print(_CLI_TOOL_HTML_INPUT_MD_REQUIRED)
        raise typer.Exit(1)
    if not output_file.endswith('.html'):
        Console.print(_CLI_TOOL_HTML_OUTPUT_HTML_REQUIRED)
        raise typer.Exit(1)

    final_title = title if title != "Problema" else FenoTitle.extract_title(Path(input_file))
    convert_markdown_to_html(final_title, Path(input_file), Path(output_file))


if __name__ == "__main__":
    app()