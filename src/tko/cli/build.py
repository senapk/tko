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
