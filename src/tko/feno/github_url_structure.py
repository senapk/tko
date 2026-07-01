from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Literal, Self
from urllib.parse import urlparse


GitHubPathType = Literal["blob", "tree"]


def _join_url(*parts: str) -> str:
    clean_parts = [part.strip("/") for part in parts if part.strip("/")]
    if not clean_parts:
        return ""
    first, *rest = clean_parts
    return "/".join([first, *rest])


@dataclass(frozen=True, slots=True)
class GitHubUrlStructure:
    user: str = ""
    repo: str = ""
    branch: str = ""
    relative_path: str = ""
    path_type: GitHubPathType | None = None

    def set_branch(self, branch: str) -> Self:
        return replace(self, branch=branch)
    
    def set_relative_path(self, relative_path: str) -> Self:
        return replace(self, relative_path=relative_path.strip("/"))

    @property
    def repository_url(self) -> str:
        return _join_url("https://github.com", self.user, self.repo)

    @property
    def branch_url(self) -> str:
        if not self.branch:
            return self.repository_url
        return _join_url(self.repository_url, "tree", self.branch)

    @property
    def github_url(self) -> str:
        if not self.branch or not self.relative_path:
            return self.branch_url

        return _join_url(
            self.repository_url,
            self.path_type or self._infer_path_type(),
            self.branch,
            self.relative_path,
        )

    @property
    def raw_github_url(self) -> str:
        if not self.branch:
            return ""
        return _join_url(
            "https://raw.githubusercontent.com",
            self.user,
            self.repo,
            self.branch,
            self.relative_path,
        )

    @property
    def relative_folder(self) -> str:
        if not self.relative_path:
            return ""

        parts = self.relative_path.split("/")
        if self.path_type == "tree":
            return self.relative_path
        if self.path_type == "blob" or "." in parts[-1]:
            return "/".join(parts[:-1])
        return self.relative_path

    @property
    def raw_base_url(self) -> str:
        if not self.branch:
            return ""
        return _join_url(
            "https://raw.githubusercontent.com",
            self.user,
            self.repo,
            self.branch,
            self.relative_folder,
        )

    @property
    def github_blob_full_url(self) -> str:
        if not self.branch:
            return self.repository_url
        return _join_url(self.repository_url, "blob", self.branch, self.relative_path)

    @property
    def github_blob_base_url(self) -> str:
        if not self.branch:
            return self.repository_url
        return _join_url(self.repository_url, "blob", self.branch, self.relative_folder)

    @property
    def github_tree_base_url(self) -> str:
        if not self.branch:
            return self.repository_url
        return _join_url(self.repository_url, "tree", self.branch, self.relative_folder)

    def with_relative_path(
        self, relative_path: str, path_type: GitHubPathType | None = None
    ) -> Self:
        return type(self)(
            user=self.user,
            repo=self.repo,
            branch=self.branch,
            relative_path=relative_path.strip("/"),
            path_type=path_type,
        )

    @classmethod
    def parse(cls, url: str) -> Self | None:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()

        parts: list[str] = [
            part
            for part in parsed.path.strip("/").split("/")
            if part
        ]

        match netloc, parts:
            case "github.com", [user, repo]:
                return cls(user=user, repo=repo.replace(".git", ""))

            case "github.com", [user, repo, ("blob" | "tree") as path_type]:
                return cls(user=user, repo=repo.replace(".git", ""), path_type=path_type)

            case "github.com", [user, repo, ("blob" | "tree") as path_type, branch, *path]:
                return cls(
                    user=user,
                    repo=repo.replace(".git", ""),
                    branch=branch,
                    relative_path="/".join(path),
                    path_type=path_type,
                )

            case "raw.githubusercontent.com", [user, repo]:
                return cls(user=user, repo=repo.replace(".git", ""))

            case "raw.githubusercontent.com", [user, repo, "refs", "heads"]:
                return cls(user=user, repo=repo.replace(".git", ""))

            case "raw.githubusercontent.com", [
                user,
                repo,
                "refs",
                "heads",
                branch,
                *path,
            ]:
                return cls(
                    user=user,
                    repo=repo.replace(".git", ""),
                    branch=branch,
                    relative_path="/".join(path),
                    path_type="blob" if path else None,
                )

            case "raw.githubusercontent.com", [user, repo, branch, *path]:
                return cls(
                    user=user,
                    repo=repo.replace(".git", ""),
                    branch=branch,
                    relative_path="/".join(path),
                    path_type="blob" if path else None,
                )

            case _:
                return None

    def _infer_path_type(self) -> GitHubPathType:
        if self.relative_path and "." not in self.relative_path.split("/")[-1]:
            return "tree"
        return "blob"
