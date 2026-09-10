import re
from tko.util.git_hub_url import GitHubUrl
from pathlib import Path, PurePosixPath
from tko.feno.task_source import activity_path_from_source_url, replace_source_comment
from tko.game.task_matcher import TaskMatcher

class LinkRebase:

    # processa o conteúdo trocando os links locais para links absolutos utilizando a url remota
    @staticmethod
    def __replace_remote(
        content: str,
        remote_raw: str,
        remote_view: str,
        remote_folder: str,
        is_local: bool = False,
        preserve_assets: bool = False,
    ) -> str:
        if not content:
            return ""

        def normalize_base(url: str) -> str:
            url = url.replace("\\", "/")
            return url if url.endswith("/") else f"{url}/"

        remote_raw = normalize_base(remote_raw)
        remote_view = normalize_base(remote_view)
        remote_folder = normalize_base(remote_folder)

        def is_asset(path: str) -> bool:
            normalized = path.replace("\\", "/").lstrip("./")
            return normalized.startswith("assets/")

        def replace_image(match: re.Match[str]) -> str:
            alt, _, path, _ = match.groups()

            if preserve_assets and is_asset(path):
                return match.group(0)

            return f"![{alt}]({remote_raw}{path})"

        def replace_folder_link(match: re.Match[str]) -> str:
            text, _, path, _ = match.groups()

            if preserve_assets and is_asset(path):
                return match.group(0)

            return f"[{text}]({remote_folder}{path})"

        def replace_link(match: re.Match[str]) -> str:
            text, _, path, _ = match.groups()

            if preserve_assets and is_asset(path):
                return match.group(0)

            return f"[{text}]({remote_view}{path})"

        result = content

        if not is_local:
            # imagens locais
            result = re.sub(
                r"!\[(.*?)\]\((\s*?)([^#:\s]+?)(\s*?)\)",
                replace_image,
                result,
            )

            # links para pasta
            result = re.sub(
                r"\[(.+?)\]\((\s*?)([^#:\s]+?/)(\s*?)\)",
                replace_folder_link,
                result,
            )

        # links locais gerais
        result = re.sub(
            r"\[(.+?)\]\((\s*?)([^#:\s]+?)(\s*?)\)",
            replace_link,
            result,
        )

        return result

    @staticmethod
    def rebase(content: str, ghu: GitHubUrl) -> str:
        relative_path = ghu.relative_path
        if relative_path and PurePosixPath(relative_path).suffix:
            parent = PurePosixPath(relative_path).parent
            ghu = ghu.set_relative_path(None if str(parent) == "." else str(parent))

        return LinkRebase.__replace_remote(
            content,
            ghu.raw_file_url,
            ghu.blob_url,
            ghu.tree_url,
            is_local=False,
        )

    @staticmethod
    def rebase_index(content: str, ghu: GitHubUrl) -> str:
        """Rebase an activity index into portable materialized-task entries.

        Ordinary Markdown links still become absolute so the copied index can
        render anywhere. Task links are different: their local link names the
        future materialized folder, while the remote URL is retained only as
        provenance for ``tko index update``.
        """
        rebased = LinkRebase.rebase(content, ghu)
        output: list[str] = []

        for line in rebased.splitlines(keepends=True):
            ending = "\n" if line.endswith("\n") else ""
            task_line = line[:-1] if ending else line
            matcher = TaskMatcher()
            if not matcher.match_pattern(task_line) or not matcher.is_url:
                output.append(line)
                continue

            try:
                folder = activity_path_from_source_url(matcher.link)
            except ValueError:
                # Non-activity checklist links retain ordinary rebase behavior.
                output.append(line)
                continue

            local_link = (folder / "README.md").as_posix()
            canonical = task_line.replace(f"({matcher.link})", f"({local_link})")
            if matcher.legacy_key_token is not None:
                canonical = canonical.replace(matcher.legacy_key_token, "", 1)
                canonical = re.sub(r"`\s+", "`", canonical, count=1)
            output.append(replace_source_comment(canonical, matcher.link) + ending)

        return "".join(output)

    @staticmethod
    def change_to_relative_folder(content: str, relative_folder: Path, preserve_assets: bool = False):
        folder = str(relative_folder)
        return LinkRebase.__replace_remote(content, folder, folder, folder, is_local = True, preserve_assets = preserve_assets)
