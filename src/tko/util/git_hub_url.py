from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Self
from urllib.parse import urlparse


def _join_url(*parts: str | None) -> str:
    return "/".join(part.strip("/") for part in parts if part)


def _normalize_path(parts: list[str]) -> str | None:
    path = "/".join(parts).strip("/")
    return path or None


@dataclass(frozen=True, slots=True)
class GitHubUrl:
    user: str = ""
    repo: str = ""
    branch: str | None = None
    relative_path: str | None = None

    def set_branch(self, branch: str | None) -> Self:
        return replace(self, branch=branch)

    def set_relative_path(self, relative_path: str | None) -> Self:
        return replace( self, relative_path=relative_path.strip("/") if relative_path else None )

    @property
    def branch_or_main(self) -> str:
        return self.branch or "main"
    
    @property
    def relative_path_or_readme(self) -> str:
        if self.relative_path is None:
            return ""
        return self.relative_path

    @property
    def repository_url(self) -> str:
        return _join_url("https://github.com", self.user, self.repo)

    @property
    def branch_tree_url(self) -> str:
        return _join_url( self.repository_url, "tree", self.branch_or_main )

    @property
    def branch_blob_url(self) -> str:
        return _join_url( self.repository_url, "blob", self.branch_or_main )

    @property
    def blob_url(self) -> str:
        return _join_url( self.repository_url, "blob", self.branch_or_main, self.relative_path_or_readme )

    @property
    def blob_root_url(self) -> str:
        return _join_url( self.repository_url, "blob", self.branch_or_main)


    @property
    def tree_url(self) -> str:
        return _join_url( self.repository_url, "tree", self.branch_or_main, self.relative_path_or_readme )

    @property
    def tree_root_url(self) -> str:
        return _join_url( self.repository_url, "tree", self.branch_or_main)

    @property
    def raw_file_url(self) -> str:
        return _join_url(
            "https://raw.githubusercontent.com",
            self.user,
            self.repo,
            self.branch_or_main,
            self.relative_path_or_readme,
        )

    @classmethod
    def parse(cls, url: str) -> Self | None:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()

        parts = [
            part
            for part in parsed.path.strip("/").split("/")
            if part
        ]

        if len(parts) >= 2:
            parts[1] = parts[1].removesuffix(".git")

        match netloc, parts:
            case "github.com", [user, repo]:
                return cls(user=user, repo=repo)

            case "github.com", [user, repo, ("blob" | "tree")]:
                return cls(user=user, repo=repo)

            case "github.com", [user, repo, ("blob" | "tree"), branch, *path]:
                return cls(
                    user=user,
                    repo=repo,
                    branch=branch,
                    relative_path=_normalize_path(path),
                )

            case "raw.githubusercontent.com", [user, repo]:
                return cls(user=user, repo=repo)

            case "raw.githubusercontent.com", [user, repo, "refs", "heads"]:
                return cls(user=user, repo=repo)

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
                    repo=repo,
                    branch=branch,
                    relative_path=_normalize_path(path),
                )

            case "raw.githubusercontent.com", [user, repo, branch, *path]:
                return cls(
                    user=user,
                    repo=repo,
                    branch=branch,
                    relative_path=_normalize_path(path),
                )

            case _:
                return None