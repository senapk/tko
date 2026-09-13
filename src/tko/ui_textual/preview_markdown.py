import re

from rich.markdown import Markdown


def render_preview_markdown(content: str) -> Markdown:
    """Display leading YAML metadata as code instead of Markdown headings."""
    match: re.Match[str] | None = re.match(
        r"\A\ufeff?---[ \t]*\r?\n(.*?)(?:^---[ \t]*|^\.\.\.[ \t]*)(?:\r?\n|\Z)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is not None:
        yaml: str = match.group(1)
        # A longer fence preserves literal backticks inside YAML block scalars.
        runs: list[str] = re.findall(r"`+", yaml)
        fence: str = "`" * max(3, max((len(run) + 1 for run in runs), default=3))
        content = f"{fence}yaml\n{yaml}{fence}\n\n{content[match.end():]}"
    return Markdown(content, code_theme="monokai", hyperlinks=False)
