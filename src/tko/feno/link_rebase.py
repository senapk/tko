import re
from tko.util.git_hub_url import GitHubUrl
from pathlib import Path

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
        return LinkRebase.__replace_remote(
            content,
            ghu.raw_file_url,
            ghu.blob_url,
            ghu.tree_url,
            is_local=False,
        )

    @staticmethod
    def change_to_relative_folder(content: str, relative_folder: Path, preserve_assets: bool = False):
        folder = str(relative_folder)
        return LinkRebase.__replace_remote(content, folder, folder, folder, is_local = True, preserve_assets = preserve_assets)
