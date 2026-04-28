import typer
from pathlib import Path
from typing import Optional

from tko.app_context import AppContext

app = typer.Typer(help="Build repository artifacts")

@app.command("tests", help="Build a test target")
def build_tests(
    ctx: typer.Context,
    target: str = typer.Argument(..., help="Target to be built"),
    target_list: list[str] = typer.Argument(..., help="Input test targets"),
    width: Optional[int] = typer.Option(None, "--width", "-w", help="Terminal width"),
    unlabel: bool = typer.Option(False, "--unlabel", "-u", help="Remove all labels"),
    number: bool = typer.Option(False, "--number", "-n", help="Number labels"),
    sort: bool = typer.Option(False, "--sort", "-s", help="Sort test cases by input size"),
    pattern: str = typer.Option("@.in @.sol", "--pattern", "-p", help="Input/output file pattern (default: '@.in @.sol')")
):
    from tko.util.param import Param
    from tko.util.pattern_loader import PatternLoader
    from tko.cmds.cmd_build import CmdBuild
    
    app_ctx: AppContext = AppContext.load_from_context(ctx)
    settings = app_ctx.settings

    PatternLoader.pattern = pattern
    manip = Param.Manip().set_unlabel(unlabel).set_to_sort(sort).set_to_number(number)
    build_cmd = CmdBuild(Path(target), [Path(x) for x in target_list], manip, settings)
    build_cmd.execute()

@app.command("all", help="Build .mapi file")
def build_all(
    targets: list[str] | None = typer.Argument(None, help="directories"),
    check: bool = typer.Option(False, "--check", "-c", help="Check if the file needs to be rebuilt"),
    brief: bool = typer.Option(False, "--brief", "-b", help="Brief mode"),
    remote: bool = typer.Option(False, "--remote", "-r", help="Search for remote.cfg and create absolute links"),
    erase: bool = typer.Option(False, "--erase", "-e", help="Erase .md and .tio temp files"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Display debug msgs")
):
    from tko.feno.build import build_all as feno_build_all
    
    if targets is None:
        targets = []
    feno_build_all([Path(x) for x in targets], remote, check, erase, brief)

@app.command("index", help="Index Readme file")
def build_index(
    index: Path = typer.Argument(..., help="Path to index Markdown file"),
    base: str = typer.Argument(..., help="Directory with the task problems"),
    save: bool = typer.Option(False, "--save", help="Save README.md task title's inside task problems"),
    load: bool = typer.Option(False, "--load", help="Load README.md task title's from task problems")
):
    from tko.feno.indexer import fix_readme
    fix_readme(
        index=Path(index), 
        base_dir=Path(base), 
        default_quest_name="sandbox", 
        verbose=True, 
        save_titles=save, 
        load_titles=load
    )

@app.command("html", help="Generate HTML file from markdown file")
def build_html(
    input_file: str = typer.Argument(..., help="Input markdown file"),
    output_file: str = typer.Argument(..., help="Output HTML file"),
    title: str = typer.Option("Problema", "--title", help="Title of the HTML file")
):
    from tko.feno.title import FenoTitle
    from tko.feno.html import convert_markdown_to_html
    
    if not input_file.endswith('.md'):
        print("Erro: O arquivo de entrada Markdown deve ter a extensão .md")
        exit(1)
    if not output_file.endswith('.html'):
        print("Erro: O arquivo de saída HTML deve ter a extensão .html")
        exit(1)

    # Allow custom title or extract from input
    final_title = title if title != "Problema" else FenoTitle.extract_title(Path(input_file))
    convert_markdown_to_html(final_title, Path(input_file), Path(output_file))

@app.command("mdpp", help="Preprocessor for markdown files")
def build_mdpp(
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
def build_older(
    targets: list[str] = typer.Argument(..., help="Target files or directories")
):
    from tko.feno.older import Older
    print(Older.find_older([Path(x) for x in targets]))

@app.command("diff", help="Show diff for 2 inputs or files")
def build_diff(
    target_a: str = typer.Argument(..., help="First target to be compared"),
    target_b: str = typer.Argument(..., help="Second target to be compared"),
    path: bool = typer.Option(False, "--path", "-f", help="Targets are paths"),
    text: bool = typer.Option(False, "--text", "-t", help="Compare two texts"),
    side: bool = typer.Option(False, "--side", "-s", help="Diff mode side-by-side"),
    down: bool = typer.Option(False, "--down", "-d", help="Diff mode up-to-down")
):
    from tko.cmds.cmd_diff import cmd_diff
    # Note: argparse had exclusive groups, Typer handles it through logic or callbacks,
    # but we can just pass them directly.
    cmd_diff(target_a, target_b, side, path)

@app.command("redirect", help="Create redirected markdown file")
def build_redirect(
    target: str = typer.Argument(..., help="Directories"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file")
):
    from tko.feno.remote_md import Absolute
    Absolute.convert_or_copy_or_print(Path(target), output if output is None else Path(output))

@app.command("filter", help="Filter code removing answers")
def build_filter(
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
        exit()

    CodeFilter.cf_single_file(Path(target), None if output is None else Path(output), update, cheat)

@app.command("drafts", help="Create drafts for TKO task using src dir")
def build_drafts(ctx: typer.Context):
    from tko.feno.filter import CodeFilter, DeepFilter
    
    # get changedir from globals
    app_ctx = AppContext.load_from_context(ctx)  # Ensure context is loaded
    changedir = app_ctx.changedir
    here = Path(changedir).resolve()
    
    print(f"Updating drafts in {here}")
    source_src = CodeFilter.get_default_src_dir(here)
    drafts_dest = CodeFilter.get_source_drafts_dir(here)
    if source_src.is_dir():
        filter_obj = DeepFilter().set_indent(4)
        filter_obj.execute(source_src, drafts_dest, 5)

if __name__ == "__main__":
    app()
