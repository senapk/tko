from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
from pathlib import Path
import subprocess
import tomllib
from typing import cast

from loguru import logger

from tko.config.languages_settings import LanguagesSettings
from tko.i18n import Msg
from tko.repository.remote import Remote
from tko.repository.repository import Repository
from tko.repository.repository_data import ConfigDict, ConfigValue, ProfileLink
from tko.util.decoder import Decoder
from tko.util.git_hub_url import GitHubUrl


_PROFILE_INVALID = Msg.text(pt="Perfil inválido: {reason}", en="Invalid profile: {reason}")
_PROFILE_UNSUPPORTED_VERSION = Msg.text(pt="versão não suportada", en="unsupported version")
_PROFILE_UNKNOWN_FIELD = Msg.text(pt="campo desconhecido: {field}", en="unknown field: {field}")
_PROFILE_NO_SOURCES = Msg.text(pt="fontes não definidas", en="sources are not defined")
_PROFILE_NO_AUTHORING = Msg.text(pt="fonte de autoria não definida", en="authoring source is not defined")
_PROFILE_AUTHORING_MISSING = Msg.text(
    pt="fonte de autoria não existe em sources",
    en="authoring source is not present in sources",
)
_PROFILE_INVALID_SOURCE = Msg.text(pt="fonte inválida: {label}", en="invalid source: {label}")
_PROFILE_INVALID_AUDIT = Msg.text(pt="auditoria inválida", en="invalid audit config")
_PROFILE_INVALID_LANGUAGE = Msg.text(pt="linguagem não suportada: {language}", en="unsupported language: {language}")
_PROFILE_LOAD_FAILED = Msg.text(pt="não foi possível carregar o perfil", en="could not load profile")
_PROFILE_UPDATE_FAILED = Msg.text(
    pt="Falha ao atualizar perfil vinculado. Usando o último perfil válido.",
    en="Failed to update linked profile. Using the last valid profile.",
)


@dataclass(frozen=True)
class LoadedProfile:
    profile: ConfigDict
    link: ProfileLink


class LinkedProfileService:
    supported_versions = {"0.1"}
    root_fields = {"version", "name", "authoring_source", "language", "audit", "sources"}
    audit_fields = {"enabled", "interval_seconds"}
    source_fields = {"uri"}

    def __init__(self, repo: Repository):
        self.repo = repo

    def load(self, uri: str, refresh_minutes: int = 60, force_git_update: bool = False) -> LoadedProfile:
        content, revision, normalized_uri = self._read_uri(uri, force_git_update=force_git_update)
        profile = self.parse_and_validate(content)
        content_hash = "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()
        link = ProfileLink(
            uri=normalized_uri,
            refresh_minutes=refresh_minutes,
            updated_at=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            revision=revision,
            content_hash=content_hash if not revision else "",
        )
        return LoadedProfile(profile=profile, link=link)

    def parse_and_validate(self, content: str) -> ConfigDict:
        try:
            raw = tomllib.loads(content)
        except tomllib.TOMLDecodeError as error:
            raise ValueError(str(_PROFILE_INVALID).format(reason=error)) from error
        if not isinstance(raw, dict):
            raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_LOAD_FAILED)))
        data = cast(ConfigDict, raw)
        self._validate_root(data)
        profile = self._profile_from_remote(data)
        self._validate_profile(profile)
        return profile

    def apply_loaded(self, loaded: LoadedProfile) -> None:
        self.repo.data.update_profile_from_dict(loaded.profile)
        self.repo.data.link = loaded.link

    def refresh_if_due(self, force: bool = False) -> bool:
        link = self.repo.data.link
        if link is None or not link.uri:
            return False
        if not force and not self._is_due(link):
            return False
        try:
            loaded = self.load(link.uri, refresh_minutes=link.refresh_minutes, force_git_update=force)
            self.apply_loaded(loaded)
            return True
        except Exception as error:
            logger.warning(str(_PROFILE_UPDATE_FAILED))
            logger.debug(error)
            return False

    def _read_uri(self, uri: str, force_git_update: bool) -> tuple[str, str, str]:
        github = GitHubUrl.parse(uri)
        if github is not None:
            if github.relative_path is None:
                github = github.set_relative_path("profile.toml")
            previous_mode = self.repo.git_cache.update_mode
            if force_git_update:
                from tko.repository.git_cache import UpdateMode

                self.repo.git_cache.update_mode = UpdateMode.ALWAYS
            try:
                path, ok = self.repo.git_cache.git_hub_url_to_path(github, load_git=True)
            finally:
                self.repo.git_cache.update_mode = previous_mode
            if not ok:
                raise ValueError(str(_PROFILE_LOAD_FAILED))
            return Decoder.load(path), self._git_revision(path.parent), github.blob_url

        path = Path(uri)
        if not path.is_absolute():
            path = (self.repo.root_dir / path).resolve()
        if not path.exists():
            raise ValueError(str(_PROFILE_LOAD_FAILED))
        return Decoder.load(path), "", path.as_posix()

    def _git_revision(self, path: Path) -> str:
        current = path
        while current != current.parent:
            if (current / ".git").exists():
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=current,
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    return result.stdout.strip()
                return ""
            current = current.parent
        return ""

    def _validate_root(self, data: ConfigDict) -> None:
        for field in data:
            if field not in self.root_fields:
                raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_UNKNOWN_FIELD).format(field=field)))
        version = data.get("version")
        if not isinstance(version, str) or version not in self.supported_versions:
            raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_UNSUPPORTED_VERSION)))

    def _profile_from_remote(self, data: ConfigDict) -> ConfigDict:
        profile: ConfigDict = {}
        for key in ("name", "authoring_source", "language", "audit", "sources"):
            if key in data:
                profile[key] = cast(ConfigValue, data[key])
        return profile

    def _validate_profile(self, profile: ConfigDict) -> None:
        authoring_source = profile.get("authoring_source")
        if not isinstance(authoring_source, str) or not authoring_source:
            raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_NO_AUTHORING)))

        sources = profile.get("sources")
        if not isinstance(sources, dict) or not sources:
            raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_NO_SOURCES)))
        if authoring_source not in sources:
            raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_AUTHORING_MISSING)))

        for label, source_data in cast(dict[str, object], sources).items():
            if not isinstance(source_data, dict):
                raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_INVALID_SOURCE).format(label=label)))
            for field in source_data:
                if field not in self.source_fields:
                    raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_UNKNOWN_FIELD).format(field=f"sources.{label}.{field}")))
            uri = source_data.get("uri")
            if not isinstance(uri, str) or not uri:
                raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_INVALID_SOURCE).format(label=label)))
            _ = Remote.from_uri(label, uri)

        audit = profile.get("audit")
        if audit is not None:
            if not isinstance(audit, dict):
                raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_INVALID_AUDIT)))
            for field in audit:
                if field not in self.audit_fields:
                    raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_UNKNOWN_FIELD).format(field=f"audit.{field}")))
            enabled = audit.get("enabled")
            interval = audit.get("interval_seconds")
            if enabled is not None and not isinstance(enabled, bool):
                raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_INVALID_AUDIT)))
            if interval is not None and (not isinstance(interval, int) or interval <= 0):
                raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_INVALID_AUDIT)))

        language = profile.get("language")
        if language is not None:
            languages = LanguagesSettings.default_lang_settings
            if not isinstance(language, str) or language not in languages:
                raise ValueError(str(_PROFILE_INVALID).format(reason=str(_PROFILE_INVALID_LANGUAGE).format(language=language)))

        previous = self.repo.data.to_dict()
        try:
            self.repo.data.update_profile_from_dict(profile)
        finally:
            self.repo.data.load_from_dict(previous)

    def _is_due(self, link: ProfileLink) -> bool:
        if not link.updated_at:
            return True
        try:
            updated = datetime.fromisoformat(link.updated_at.replace("Z", "+00:00"))
        except ValueError:
            return True
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=UTC)
        return datetime.now(UTC) - updated >= timedelta(minutes=max(1, link.refresh_minutes))
