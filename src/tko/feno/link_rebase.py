import re
from tko.feno.github_cfg import GithubCfg
from tko.feno.github_url_structure import GithubUrlStructure
from tko.util.decoder import Decoder
from pathlib import Path

class LinkRebase:

    # processa o conteúdo trocando os links locais para links absolutos utilizando a url remota
    @staticmethod
    def __replace_remote(content: str, remote_raw: str, remote_view: str, remote_folder: str, is_local: bool = False) -> str:
        sep = "/"
        remote_view = remote_view.replace("\\", "/")
        remote_folder = remote_folder.replace("\\", "/")
        remote_raw = remote_raw.replace("\\", "/")
        if content == "":
            return ""
        if not remote_raw.endswith("/"):
            remote_raw += sep
        if not remote_view.endswith("/"):
            remote_view += sep
        if not remote_folder.endswith("/"):
            remote_folder += sep

        result = content
        if not is_local:
            #trocando todas as imagens com link local
            regex = r"!\[(.*?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
            subst = r"![\1](" + remote_raw + r"\3)"
            result = re.sub(regex, subst, result, count=0, flags=0)

            regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?/)\)"
            subst = r"[\1](" + remote_folder + r"\3)"
            result = re.sub(regex, subst, result, 0)

        #trocando todos os links locais cujo conteudo nao seja vazio
        regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
        subst = r"[\1](" + remote_view + r"\3)"
        result = re.sub(regex, subst, result, 0)

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
    def change_to_relative_folder(content: str, relative_folder: Path):
        folder = str(relative_folder)
        return LinkRebase.__replace_remote(content, folder, folder, folder, is_local = True)

    @staticmethod
    def convert_or_copy_or_print(source: Path, target: Path | None, make_remote: bool = False):
        content: str = Decoder.load(source)
        cfg = GithubCfg(source, make_remote)
        if cfg.cfg_exists():
            content = LinkRebase.rebase(content, cfg.calc_link_for_local_file())
        if target is not None:
            Decoder.save(target, content)
        else:
            print(content)
