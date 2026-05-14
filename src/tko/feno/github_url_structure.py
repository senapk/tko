from __future__ import annotations
from urllib.parse import urlparse


class GithubUrlStructure:
    def __init__(self):
        self.user: str = ""
        self.repo: str = ""
        self.branch: str = ""
        self.relative_path: str = ""

    @property
    def repository_url(self) -> str:
        return f"https://github.com/{self.user}/{self.repo}"

    @property
    def github_url(self) -> str:
        return (
            f"https://github.com/"
            f"{self.user}/{self.repo}/blob/"
            f"{self.branch}/{self.relative_path}"
        )
    
    @property
    def raw_github_url(self) -> str:
        return (
            f"https://raw.githubusercontent.com/"
            f"{self.user}/{self.repo}/"
            f"{self.branch}/{self.relative_path}"
        )
    
    def parse(self, url: str) -> bool:
        parsed = urlparse(url)

        parts: list[str] = [
            part
            for part in parsed.path.strip("/").split("/")
            if part
        ]

        match parsed.netloc, parts:
            case (
                "raw.githubusercontent.com", [user, repo, "refs", "heads", branch, *path],
            ):
                self.user = user
                self.repo = repo
                self.branch = branch
                self.relative_path = "/".join(path)
                return True 

            case (
                "github.com", [user, repo, ("blob" | "tree"), branch, *path],
            ):
                self.user = user
                self.repo = repo
                self.branch = branch
                self.relative_path = "/".join(path)
                return True

            case _:
                return False