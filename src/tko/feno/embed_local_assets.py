"""Embed task-local file references in Markdown as data URIs."""

from __future__ import annotations

import base64
import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


class LocalAssetError(ValueError):
    """Raised when a local Markdown reference cannot be packaged safely."""


_FENCE_START = re.compile(r"^[ ]{0,3}(?P<fence>`{3,}|~{3,})")
_REFERENCE = re.compile(
    r"(?m)^(?P<prefix>[ \t]{0,3}\[[^\]\n]+\]:[ \t]*)"
    r"(?P<destination><[^>\n]+>|[^\s\n]+)(?P<suffix>[^\n]*)$"
)
_HTML_TAG = re.compile(r"<[A-Za-z][A-Za-z0-9:-]*(?:\s+[^<>]*?)?\s*/?>", re.DOTALL)
_HTML_ATTRIBUTE = re.compile(
    r"(?P<prefix>\b(?:src|href)\s*=\s*)"
    r"(?:(?P<quote>[\"'])(?P<quoted>.*?)(?P=quote)|(?P<unquoted>[^\s>]+))",
    re.IGNORECASE | re.DOTALL,
)
_MARKDOWN_ESCAPABLE = frozenset(r"!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~")


def _unescape_path(path: str) -> str:
    output: list[str] = []
    cursor: int = 0
    while cursor < len(path):
        if path[cursor] == "\\" and cursor + 1 < len(path) and path[cursor + 1] in _MARKDOWN_ESCAPABLE:
            output.append(path[cursor + 1])
            cursor += 2
        else:
            output.append(path[cursor])
            cursor += 1
    return "".join(output)


class _AssetResolver:
    def __init__(self, activity_dir: Path, embed: bool) -> None:
        self.activity_dir: Path = activity_dir.resolve()
        self.embed: bool = embed

    def rewrite(self, destination: str) -> str:
        parsed = urlsplit(destination)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return destination

        decoded_path: str = unquote(_unescape_path(parsed.path).replace("\\", "/"))
        relative_path: str = decoded_path.lstrip("/")
        target: Path = (self.activity_dir / relative_path).resolve()
        try:
            target.relative_to(self.activity_dir)
        except ValueError as error:
            raise LocalAssetError(
                f"local reference escapes the activity folder: {destination}"
            ) from error

        if not target.exists():
            raise LocalAssetError(f"local reference does not exist: {destination}")
        if target.is_dir():
            return destination
        if not target.is_file():
            raise LocalAssetError(f"local reference is not a regular file: {destination}")
        if not self.embed:
            return destination

        mime_type: str = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        encoded: str = base64.b64encode(target.read_bytes()).decode("ascii")
        data_uri: str = f"data:{mime_type};base64,{encoded}"
        if parsed.fragment:
            data_uri += f"#{parsed.fragment}"
        return data_uri


def _rewrite_destination(destination: str, resolver: _AssetResolver) -> str:
    if destination.startswith("<") and destination.endswith(">"):
        return f"<{resolver.rewrite(destination[1:-1])}>"
    return resolver.rewrite(destination)


def _rewrite_html_tag(tag: str, resolver: _AssetResolver) -> str:
    def replace_attribute(match: re.Match[str]) -> str:
        quoted: str | None = match.group("quoted")
        unquoted: str | None = match.group("unquoted")
        destination: str = quoted if quoted is not None else (unquoted or "")
        rewritten: str = resolver.rewrite(destination)
        if quoted is not None:
            quote: str = match.group("quote") or '"'
            return f"{match.group('prefix')}{quote}{rewritten}{quote}"
        return f"{match.group('prefix')}{rewritten}"

    return _HTML_ATTRIBUTE.sub(replace_attribute, tag)


def _closing_bracket(text: str, start: int) -> int | None:
    depth: int = 0
    escaped: bool = False
    for index in range(start, len(text)):
        character: str = text[index]
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "[":
            depth += 1
        elif character == "]":
            depth -= 1
            if depth == 0:
                return index
    return None


def _inline_destination_span(text: str, opening: int) -> tuple[int, int] | None:
    cursor: int = opening + 1
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    if cursor >= len(text):
        return None

    if text[cursor] == "<":
        destination_start: int = cursor + 1
        cursor = destination_start
        escaped: bool = False
        while cursor < len(text):
            character: str = text[cursor]
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == ">":
                destination_end: int = cursor
                cursor += 1
                break
            cursor += 1
        else:
            return None
    else:
        destination_start = cursor
        nesting: int = 0
        while cursor < len(text):
            character = text[cursor]
            if character == "\\":
                cursor += 2
                continue
            if character == "(":
                nesting += 1
            elif character == ")":
                if nesting == 0:
                    break
                nesting -= 1
            elif character.isspace() and nesting == 0:
                break
            cursor += 1
        destination_end = cursor

    quote: str | None = None
    nesting = 0
    escaped = False
    for closing in range(cursor, len(text)):
        character = text[closing]
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif quote is not None:
            if character == quote:
                quote = None
        elif character in {'"', "'"}:
            quote = character
        elif character == "(":
            nesting += 1
        elif character == ")":
            if nesting == 0:
                return destination_start, destination_end
            nesting -= 1
    return None


def _rewrite_inline_links(text: str, resolver: _AssetResolver) -> str:
    output: list[str] = []
    cursor: int = 0
    while cursor < len(text):
        if text[cursor] == "\\" and cursor + 1 < len(text):
            output.append(text[cursor:cursor + 2])
            cursor += 2
            continue
        image_prefix: int = 1 if text.startswith("![", cursor) else 0
        bracket_start: int = cursor + image_prefix
        if text[bracket_start:bracket_start + 1] != "[":
            output.append(text[cursor])
            cursor += 1
            continue

        close_bracket: int | None = _closing_bracket(text, bracket_start)
        if close_bracket is None or close_bracket + 1 >= len(text) or text[close_bracket + 1] != "(":
            output.append(text[cursor])
            cursor += 1
            continue

        span: tuple[int, int] | None = _inline_destination_span(text, close_bracket + 1)
        if span is None:
            output.append(text[cursor])
            cursor += 1
            continue

        destination_start, destination_end = span
        output.append(text[cursor:destination_start])
        destination: str = text[destination_start:destination_end]
        output.append(resolver.rewrite(destination))
        cursor = destination_end
    return "".join(output)


def _rewrite_markup(markup: str, resolver: _AssetResolver) -> str:
    markup = _HTML_TAG.sub(lambda match: _rewrite_html_tag(match.group(0), resolver), markup)
    markup = _REFERENCE.sub(
        lambda match: (
            f"{match.group('prefix')}"
            f"{_rewrite_destination(match.group('destination'), resolver)}"
            f"{match.group('suffix')}"
        ),
        markup,
    )
    return _rewrite_inline_links(markup, resolver)


def _rewrite_prose(prose: str, resolver: _AssetResolver) -> str:
    output: list[str] = []
    cursor: int = 0
    while cursor < len(prose):
        if prose[cursor] != "`":
            next_tick: int = prose.find("`", cursor)
            if next_tick == -1:
                output.append(_rewrite_markup(prose[cursor:], resolver))
                break
            output.append(_rewrite_markup(prose[cursor:next_tick], resolver))
            cursor = next_tick
            continue

        delimiter_end: int = cursor
        while delimiter_end < len(prose) and prose[delimiter_end] == "`":
            delimiter_end += 1
        delimiter: str = prose[cursor:delimiter_end]
        close_tick: int = prose.find(delimiter, delimiter_end)
        if close_tick == -1:
            output.append(_rewrite_markup(prose[cursor:], resolver))
            break
        output.append(prose[cursor:close_tick + len(delimiter)])
        cursor = close_tick + len(delimiter)
    return "".join(output)


def _rewrite_markdown(content: str, resolver: _AssetResolver) -> str:
    output: list[str] = []
    prose: list[str] = []
    fence_character: str | None = None
    fence_length: int = 0

    def flush_prose() -> None:
        if prose:
            output.append(_rewrite_prose("".join(prose), resolver))
            prose.clear()

    for line in content.splitlines(keepends=True):
        fence_match = _FENCE_START.match(line)
        if fence_character is not None:
            output.append(line)
            if fence_match is not None:
                marker: str = fence_match.group("fence")
                if marker[0] == fence_character and len(marker) >= fence_length and not line[fence_match.end():].strip():
                    fence_character = None
                    fence_length = 0
            continue
        if fence_match is not None:
            flush_prose()
            output.append(line)
            marker = fence_match.group("fence")
            fence_character = marker[0]
            fence_length = len(marker)
            continue
        prose.append(line)

    flush_prose()
    return "".join(output)


def embed_local_assets(content: str, activity_dir: Path) -> str:
    """Return Markdown with task-local file links encoded as Base64 data URIs."""
    return _rewrite_markdown(content, _AssetResolver(activity_dir, embed=True))


def validate_local_assets(content: str, activity_dir: Path) -> None:
    """Validate local references without reading or encoding the referenced files."""
    _rewrite_markdown(content, _AssetResolver(activity_dir, embed=False))
