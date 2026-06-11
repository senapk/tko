import re
from tko.feno.github_cfg import GithubCfg
from tko.feno.github_url_structure import GithubUrlStructure
from tko.util.decoder import Decoder
from pathlib import Path
from tko.util.console import Console

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
    def rebase(content: str, rl: GithubUrlStructure) -> str:
        parts = rl.relative_path.split("/")
        if parts and "." in parts[-1]:
            folder = "/".join(parts[:-1])
        else:
            folder = rl.relative_path
        
        user_repo = "/".join([rl.user, rl.repo])
        remote_raw    = "/".join(["https://raw.githubusercontent.com", user_repo, rl.branch , folder])
        remote_view    = "/".join(["https://github.com", user_repo, "blob", rl.branch, folder])
        remote_folder = "/".join(["https://github.com", user_repo, "tree", rl.branch, folder])
        return LinkRebase.__replace_remote(content, remote_raw, remote_view, remote_folder, is_local = False)

    @staticmethod
    def change_to_relative_folder(content: str, relative_folder: Path, preserve_assets: bool = False):
        folder = str(relative_folder)
        return LinkRebase.__replace_remote(content, folder, folder, folder, is_local = True, preserve_assets = preserve_assets)

    @staticmethod
    def convert_or_copy_or_print(source: Path, target: Path | None, make_remote: bool = False):
        content: str = Decoder.load(source)
        cfg = GithubCfg(source, make_remote)
        if cfg.cfg_exists():
            content = LinkRebase.rebase(content, cfg.calc_link_for_local_file())
        if target is not None:
            Decoder.save(target, content)
        else:
            Console.print(content)
