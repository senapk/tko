
import os
import re
import configparser

from typing import List, Optional
import urllib.request

class Title:
    @staticmethod
    def extract_title(readme_file):
        title = open(readme_file).read().split("\n")[0]
        parts = title.split(" ")
        if parts[0].count("#") == len(parts[0]):
            del parts[0]
        title = " ".join(parts)
        return title

class RemoteCfg:
    def __init__(self, url: Optional[str] = None):
        self.user = ""
        self.repo = ""
        self.branch = ""
        self.folder = ""
        self.file = ""
        if url is not None:
            self.from_url(url)

    def from_url(self, url: str):
        if url.startswith("https://raw.githubusercontent.com/"):
            url = url.replace("https://raw.githubusercontent.com/", "")
            parts = url.split("/")
            self.user = parts[0]
            self.repo = parts[1]
            self.branch = parts[2]
            self.folder = "/".join(parts[3:-1])
            self.file = parts[-1]
        elif url.startswith("https://github.com/"):
            url = url.replace("https://github.com/", "")
            parts = url.split("/")
            self.user = parts[0]
            self.repo = parts[1]
            self.branch = parts[3]
            self.folder = "/".join(parts[4:-1])
            self.file = parts[-1]
        else:
            raise Exception("Invalid URL")

    def get_raw_url(self):
        return "https://raw.githubusercontent.com/" + self.user + "/" + self.repo + "/" + self.branch + "/" + self.folder + "/" + self.file

    def download_absolute(self, filename: str):
        try:
            [tempfile, __content] = urllib.request.urlretrieve(self.get_raw_url(), filename)
            content = ""
            try:
                content = open(tempfile, encoding="utf-8").read()
            except:
                content = open(tempfile).read()
            with open(filename, "w", encoding="utf-8") as f:
                absolute = Absolute.relative_to_absolute(content, self)
                f.write(absolute.encode("utf-8").decode("utf-8"))
        except urllib.error.HTTPError:
            print("Error downloading file", self.get_raw_url())
            return

    def __str__(self):
        return f"user: ({self.user}), repo: ({self.repo}), branch: ({self.branch}), folder: ({self.folder}), file: ({self.file})"

    def read(self, cfg_path: str):
        if not os.path.isfile(cfg_path):
            print("no remote.cfg found")

        config = configparser.ConfigParser()
        config.read(cfg_path)

        self.user   = config["DEFAULT"]["user"]
        self.repo   = config["DEFAULT"]["rep"]
        self.branch = config["DEFAULT"]["branch"]
        self.folder = config["DEFAULT"]["base"]
        self.tag    = config["DEFAULT"]["tag"]

    @staticmethod
    def search_cfg_path(source_dir) -> Optional[str]:
        # look for the remote.cfg file in the current folder
        # if not found, look for it in the parent folder
        # if not found, look for it in the parent's parent folder ...

        path = os.path.abspath(source_dir)
        while path != "/":
            cfg_path = os.path.join(path, "remote.cfg")
            if os.path.isfile(cfg_path):
                return cfg_path
            path = os.path.dirname(path)
        return None

class Absolute:

    # processa o conteúdo trocando os links locais para links absolutos utilizando a url remota
    @staticmethod
    def __replace_remote(content: str, remote_raw: str, remote_view: str, remote_folder: str) -> str:
        if content is None or content == "":
            return ""
        if not remote_raw.endswith("/"):
            remote_raw += "/"
        if not remote_view.endswith("/"):
            remote_view += "/"
        if not remote_folder.endswith("/"):
            remote_folder += "/"

        #trocando todas as imagens com link local
        regex = r"!\[(.*?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
        subst = r"![\1](" + remote_raw + r"\3)"
        result = re.sub(regex, subst, content, 0)


        regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?/)\)"
        subst = r"[\1](" + remote_folder + r"\3)"
        result = re.sub(regex, subst, result, 0)

        #trocando todos os links locais cujo conteudo nao seja vazio
        regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
        subst = r"[\1](" + remote_view + r"\3)"
        result = re.sub(regex, subst, result, 0)

        return result

    @staticmethod
    def relative_to_absolute(content: str, cfg: RemoteCfg):
        user_repo = cfg.user + "/" + cfg.repo
        raw = "https://raw.githubusercontent.com"
        github = "https://github.com"
        remote_raw    = f"{raw}/{user_repo}/{cfg.branch}/{cfg.folder}"
        remote_view    = f"{github}/{user_repo}/blob/{cfg.branch}/{cfg.folder}"
        remote_folder = f"{github}/{user_repo}/tree/{cfg.branch}/{cfg.folder}"
        return Absolute.__replace_remote(content, remote_raw, remote_view, remote_folder)

    @staticmethod
    def from_file(source_file, output_file, cfg: RemoteCfg, hook):
        content = open(source_file, encoding="utf-8").read()
        content = Absolute.relative_to_absolute(content, cfg)
        open(output_file, "w").write(content)
        
class RemoteMd:

    # @staticmethod
    # def insert_preamble(lines: List[str], online: str, tkodown: str) -> List[str]:

    #     text = "\n- Veja a versão online: [aqui.](" + online + ")\n"
    #     text += "- Para programar na sua máquina (local/virtual) use:\n"
    #     text += "  - `" + tkodown + "`\n"
    #     text += "- Se não tem o `tko`, instale pelo [LINK](https://github.com/senapk/tko#tko).\n\n---"

    #     lines.insert(1, text)

    #     return lines

    # @staticmethod
    # def insert_qxcode_preamble(cfg: RemoteCfg, content: str, hook) -> str:
    #     base_hook = os.path.join(cfg.base, hook)

    #     lines = content.split("\n")
    #     online_readme_link = os.path.join("https://github.com", cfg.user, cfg.repo, "blob", cfg.branch, base_hook, "Readme.md")
    #     tkodown = "tko down " + cfg.tag + " " + hook
    #     lines = RemoteMd.insert_preamble(lines, online_readme_link, tkodown)
    #     return "\n".join(lines)

    @staticmethod
    def run(remote_cfg: RemoteCfg, source: str, target: str, hook) -> bool:    
        content = open(source).read()
        content = Absolute.relative_to_absolute(content, remote_cfg)
        open(target, "w").write(content)
        return True
