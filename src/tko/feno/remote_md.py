import os
import re
import configparser
import argparse
from tko.util.decoder import Decoder
from tko.util.text import Text

class RemoteLink:
    def __init__(self):
        self.user = ""
        self.repo = ""
        self.branch = ""
        self.folder = ""
        self.file = ""

    def identify_from_url(self, url: str):
        if url.startswith("https://raw.githubusercontent.com"):
            url = url.replace("https://raw.githubusercontent.com/", "")
            elements = url.split("/")
            self.user = elements[0]
            self.repo = elements[1]
            if elements[2] != "refs":
                raise ValueError("Invalid URL")
            if elements[3] != "heads":
                raise ValueError("Invalid URL")
            self.branch = elements[4]
            self.folder = "/".join(elements[5:-1])
            self.file = elements[-1]
        elif url.endswith(".md"):
            url = url.replace("https://github.com/", "")
            elements = url.split("/")
            self.user = elements[0]
            self.repo = elements[1]
            if elements[2] != "blob":
                raise ValueError("Invalid URL")
            self.branch = elements[3]
            self.folder = "/".join(elements[4:-1])
            self.file = elements[-1]
        else:
            url = url.replace("https://github.com/", "")
            elements = url.split("/")
            self.user = elements[0]
            self.repo = elements[1]
            if elements[2] != "tree":
                raise ValueError("Invalid URL")
            self.branch = elements[3]
            self.folder = "/".join(elements[4:])
        return self

class RemoteCfg:
    def __init__(self, target: str, make_remote: bool):
        self.target = target
        self.remote: RemoteLink = RemoteLink()
        self.cfg_path: str | None = None
        if make_remote:
            self.__load_cfg_path(target)
            self.__parse_cfg()
            if self.cfg_path is None:
                print(Text.format("{r}: remote.cfg file not set", "fail"))

    def cfg_exists(self):
        return self.cfg_path is not None

    def get_cfg_path(self):
        if self.cfg_path is None:
            raise Exception("cfg_path not set")
        return self.cfg_path

    def calc_link_for_local_file(self):
        base_cfg_file = os.path.dirname(os.path.abspath(self.get_cfg_path()))
        base_source_file = os.path.dirname(os.path.abspath(self.target))
        if not base_source_file.startswith(base_cfg_file):
            raise Exception("File not match with remote cfg")
        folder = os.path.relpath(base_source_file, base_cfg_file)
        self.remote.folder = folder
        return self.remote

    def __parse_cfg(self):
        if self.cfg_path is None:
            return
        config = configparser.ConfigParser()
        config.read(self.get_cfg_path())

        self.remote.user = config["DEFAULT"]["user"]
        self.remote.repo = config["DEFAULT"]["rep"]
        self.remote.branch = config["DEFAULT"]["branch"]

    def __load_cfg_path(self, target: str):
        # look for the remote.cfg file in the current folder
        # if not found, look for it in the parent folder
        # if not found, look for it in the parent's parent folder ...

        path = os.path.dirname(os.path.abspath(target))

        while True:
            cfg_path = os.path.join(path, "remote.cfg")
            if os.path.isfile(cfg_path):
                self.cfg_path = cfg_path
                break
            new_path = os.path.dirname(path)
            if new_path == path:
                break
            path = new_path


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
        result = re.sub(regex, subst, content, count=0, flags=0)

        regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?/)\)"
        subst = r"[\1](" + remote_folder + r"\3)"
        result = re.sub(regex, subst, result, 0)

        #trocando todos os links locais cujo conteudo nao seja vazio
        regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
        subst = r"[\1](" + remote_view + r"\3)"
        result = re.sub(regex, subst, result, 0)

        return result

    @staticmethod
    def relative_to_absolute(content: str, rl: RemoteLink):
        folder = rl.folder
        user_repo = "/".join([rl.user, rl.repo])
        remote_raw    = "/".join(["https://raw.githubusercontent.com", user_repo, rl.branch , folder])
        remote_view    = "/".join(["https://github.com", user_repo, "blob", rl.branch, folder])
        remote_folder = "/".join(["https://github.com", user_repo, "tree", rl.branch, folder])
        return Absolute.__replace_remote(content, remote_raw, remote_view, remote_folder)


    @staticmethod
    def convert_or_copy_or_print(source: str, target: str | None, make_remote: bool = False):
        content = Decoder.load(source)
        cfg = RemoteCfg(source, make_remote)
        if cfg.cfg_exists():
            content = Absolute.relative_to_absolute(content, cfg.calc_link_for_local_file())
        if target is not None:
            Decoder.save(target, content)
        else:
            print(content)
        

def remote_main(args):
    Absolute.convert_or_copy_or_print(args.target, args.output)
