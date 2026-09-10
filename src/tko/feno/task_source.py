"""Remote-origin metadata for materialized activity tasks.

The activity link remains the location used by the game.  A ``source`` comment
is deliberately only provenance for the index materialization commands.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from tko.util.git_hub_url import GitHubUrl


# ``source:`` was the first public spelling. Keep accepting it so an index can
# be normalized in place, while every writer emits the field-style ``source=``.
_SOURCE_COMMENT_RE = re.compile(r"<!--\s*source\s*(?:=|:)\s*(?P<url>\S+)\s*-->")


def validate_source_url(url: str) -> str:
    """Validate and return a GitHub URL for an activity ``README.md``.

    Materialized tasks have one intentionally narrow kind of remote origin.
    Keeping this check here means the CLI and indexer cannot drift apart.
    """
    parsed = urlparse(url)
    github = GitHubUrl.parse(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc.lower() != "github.com"
        or github is None
        or github.relative_path is None
        or "/blob/" not in parsed.path
        or not parsed.path.rstrip("/").endswith("/README.md")
    ):
        raise ValueError(f"Task source must point to a GitHub README.md: {url}")
    return url


def activity_path_from_source_url(url: str) -> Path:
    """Return the materialized activity folder encoded by a GitHub README URL."""
    github = GitHubUrl.parse(validate_source_url(url))
    assert github is not None and github.relative_path is not None
    readme = Path(github.relative_path)
    folder = readme.parent
    if folder == Path(".") or folder.is_absolute() or ".." in folder.parts:
        raise ValueError("Task source README.md must be inside an activity folder")
    return folder


def activity_path_from_local_link(link: str) -> Path:
    """Return the task folder for a canonical, index-relative README link."""
    readme = Path(link)
    folder = readme.parent
    if (
        readme.is_absolute()
        or readme.name != "README.md"
        or folder == Path(".")
        or ".." in readme.parts
    ):
        raise ValueError(f"Task must point to a relative activity README.md: {link}")
    return folder


def source_url_from_line(line: str) -> str | None:
    """Read and validate the optional remote-origin comment in a task line."""
    matches = list(_SOURCE_COMMENT_RE.finditer(line))
    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError("A task may contain only one source comment")
    return validate_source_url(matches[0].group("url"))


def strip_source_comments(text: str) -> str:
    """Remove provenance comments before task fields and variables are parsed."""
    return _SOURCE_COMMENT_RE.sub("", text)


def source_comment(url: str) -> str:
    """Return the sole canonical representation of a validated source URL."""
    return f"<!-- source={validate_source_url(url)} -->"


def replace_source_comment(line: str, url: str) -> str:
    """Replace optional source metadata with one canonical trailing comment."""
    # Parse first so malformed or duplicated existing provenance is never hidden.
    source_url_from_line(line)
    without_source = _SOURCE_COMMENT_RE.sub("", line).rstrip()
    return f"{without_source} {source_comment(url)}"
