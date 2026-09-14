from __future__ import annotations
from collections.abc import Mapping, Sized
import os
import tempfile
import time
import tomllib
from pathlib import Path
from typing import cast
from tko.util.decoder import Decoder
from tko.i18n import Msg
from tko.repository.repository import Repository
from tko.repository.repository_data import ConfigDict, ConfigValue
from tko.repository.task_data_format import MigrationRequiredError, initialize_task_data


_REPOSITORY_LOADER_GIT_CONFLICT = Msg.text(
    pt="Conflito de merge git detectado em {file}.\nResolva o conflito manualmente antes de continuar.",
    en="Git merge conflict detected in {file}.\nPlease resolve the conflict manually before continuing.",
)
_REPOSITORY_LOADER_EMPTY_CONFIG_FILE = Msg.text(
    pt="Arquivo de configuração vazio: {file}",
    en="Empty config file: {file}",
)
_REPOSITORY_LOADER_CONFIG_EMPTY = Msg.parse(
    pt="O arquivo de configuração do repositório [y]{file}[] está [r]vazio[].\nAbra e corrija o conteúdo ou crie um novo.",
    en="The repository configuration file [y]{file}[] is [r]empty[].\nOpen and fix the content or create a new one.",
)
_REPOSITORY_LOADER_CONFIG_CORRUPTED_UNEXPECTED = Msg.parse(
    pt="O arquivo de configuração do repositório [y]{file}[] está [r]corrompido[].\nErro inesperado: {error}\nAbra e corrija o conteúdo ou crie um novo.",
    en="The repository configuration file [y]{file}[] is [r]corrupted[].\nUnexpected error: {error}\nOpen and fix the content or create a new one.",
)

class ConfigMergeConflictError(Exception):
    pass

def _toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        values = cast(list[object], value)
        return "[" + ", ".join(_toml_value(item) for item in values) + "]"
    if value is None:
        return '""'
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'

def _toml_key(key: object) -> str:
    text = str(key)
    if text and text.replace("_", "").replace("-", "").isalnum() and not text[0].isdigit():
        return text
    return _toml_value(text)

def _config_dict(value: object) -> ConfigDict | None:
    if not isinstance(value, Mapping):
        return None
    output: ConfigDict = {}
    mapping = cast(Mapping[object, object], value)
    for key, item in mapping.items():
        if not isinstance(key, str):
            return None
        output[key] = cast(ConfigValue, item)
    return output

def _string_dict(data: ConfigDict) -> dict[str, str]:
    return {key: value for key, value in data.items() if isinstance(value, str)}

def dumps_repository_toml(data: ConfigDict) -> str:
    lines: list[str] = []
    lines.append(f"version = {_toml_value(data.get('version', '0.3'))}")
    lines.append("")

    link = _config_dict(data.get("link"))
    if link is not None:
        lines.append("[link]")
        for key in ("uri", "refresh_minutes", "updated_at", "revision", "content_hash"):
            value = link.get(key)
            if value not in (None, ""):
                lines.append(f"{_toml_key(key)} = {_toml_value(value)}")
        lines.append("")

    profile = _config_dict(data.get("profile"))
    if profile is not None:
        lines.append("[profile]")
        if profile.get("name"):
            lines.append(f"name = {_toml_value(profile.get('name', ''))}")
        lines.append(f"authoring_source = {_toml_value(profile.get('authoring_source', ''))}")
        if profile.get("language"):
            lines.append(f"language = {_toml_value(profile.get('language', ''))}")
        lines.append("")
        sources = _config_dict(profile.get("sources"))
        if sources is not None:
            for label, source_value in sources.items():
                source = _config_dict(source_value)
                if source is None:
                    continue
                lines.append(f"[profile.sources.{_toml_key(label)}]")
                lines.append(f"uri = {_toml_value(source.get('uri', ''))}")
                lines.append("")
        audit = _config_dict(profile.get("audit"))
        if audit is not None:
            lines.append("[profile.audit]")
            for key, value in audit.items():
                if value is not None:
                    lines.append(f"{_toml_key(key)} = {_toml_value(value)}")
            lines.append("")

    preferences = _config_dict(data.get("preferences"))
    if preferences is not None:
        lines.append("[preferences]")
        for key, value in preferences.items():
            lines.append(f"{_toml_key(key)} = {_toml_value(value)}")
        lines.append("")

    state = _config_dict(data.get("state"))
    if state is not None:
        lines.append("[state]")
        for key, value in state.items():
            lines.append(f"{_toml_key(key)} = {_toml_value(value)}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

def atomic_write_toml(path: Path, data: ConfigDict) -> None:
    path = Path(path).resolve()
    dir_path = path.parent
    dir_path.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=dir_path, delete=False, suffix=".tmp") as f:
            tmp_path = Path(f.name)
            _ = f.write(dumps_repository_toml(data))
            f.flush()
            os.fsync(f.fileno())
        for attempt in range(3):
            try:
                _ = os.replace(tmp_path, path)
                break
            except PermissionError:
                if attempt < 2:
                    time.sleep(0.05 * (attempt + 1))
                else:
                    raise
        if os.name == "posix":
            dir_fd = os.open(str(dir_path), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    except Exception:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise

class RepositoryLoader:
    def __init__(self, repo: Repository) -> None:
        self.repo: Repository = repo
        self._cached_output: ConfigDict = {}  # Cache the output in the Repository instance

    def _check_for_merge_conflicts(self, content: str) -> None:
        lines = content.splitlines()
        for line in lines:
            if line.startswith("<<<<<<<") or line.startswith("=======") or line.startswith(">>>>>>>"):
                raise ConfigMergeConflictError(_REPOSITORY_LOADER_GIT_CONFLICT.t().format(file=self.repo.paths.config_file))

    @staticmethod
    def _length(data: object) -> int:
        return len(data) if isinstance(data, Sized) else 0

    @staticmethod
    def _is_config_dict(data: object) -> bool:
        return _config_dict(data) is not None

    def _load_config_dict(self, data: object, path: Path) -> ConfigDict:
        parsed = _config_dict(data)
        if parsed is not None and self._length(parsed) > 0:
            return parsed
        raise FileNotFoundError(_REPOSITORY_LOADER_EMPTY_CONFIG_FILE.t().format(file=path))

    def load(self) -> RepositoryLoader:
        path = self.repo.paths.config_file
        legacy_path = self.repo.paths.legacy_config_file
        if legacy_path.exists():
            raise MigrationRequiredError(f"Configuração antiga precisa de migração. Execute: tko tool migrate \"{path.parent.parent}\"")
        if not path.exists():
            _ = self.save(force=True)
            self._cached_output = self.repo.data.to_dict()
            return self
        content = Decoder.load(path)
        self._check_for_merge_conflicts(content)

        local_data: ConfigDict
        try:
            parsed_data: object
            parsed_data = tomllib.loads(content)

            parsed_config = _config_dict(parsed_data)
            if parsed_config is not None and self._length(parsed_config) > 0:
                local_data = parsed_config
            else:
                backup_content = Decoder.load(self.repo.paths.config_backup_file)
                self._check_for_merge_conflicts(backup_content)
                parsed_backup: object = tomllib.loads(backup_content)
                local_data = self._load_config_dict(parsed_backup, path)

        except ConfigMergeConflictError:
            raise
        except tomllib.TOMLDecodeError as e:
            raise Warning(_REPOSITORY_LOADER_CONFIG_CORRUPTED_UNEXPECTED.t().format(file=path, error=e))
        except FileNotFoundError:
            raise Warning(_REPOSITORY_LOADER_CONFIG_EMPTY.t().format(file=path))
        except Exception as e:
            raise Warning(_REPOSITORY_LOADER_CONFIG_CORRUPTED_UNEXPECTED.t().format(file=path, error=e))

        self.repo.data.load_from_dict(local_data)
        if getattr(self.repo.data, "is_linked", False):
            from tko.repository.linked_profile import LinkedProfileService

            if LinkedProfileService(self.repo).refresh_if_due(force=False):
                atomic_write_toml(path, self.repo.data.to_dict())
        self.repo.flags.from_dict(_string_dict(self.repo.data.flags))
        # Cache the output after loading
        self._cached_output = self.repo.data.to_dict()
        return self

    @staticmethod
    def _without_volatile_fields(data: ConfigDict) -> ConfigDict:
        normalized = data.copy()
        state = normalized.get("state")
        state_dict = _config_dict(state)
        if state_dict is not None:
            normalized_state = state_dict.copy()
            _ = normalized_state.pop("selected", None)
            _ = normalized_state.pop("selected_index", None)
            normalized["state"] = normalized_state
        return normalized

    def save(self, force: bool = False) -> RepositoryLoader:
        self.repo.data.version = "0.3"
        self.repo.data.flags = {key: value for key, value in self.repo.flags.to_dict().items()}
        if hasattr(self.repo.data, "validate_authoring_source"):
            self.repo.data.validate_authoring_source()

        path: Path = Path(self.repo.paths.config_file)
        payload = self.repo.data.to_dict()

        # Compare with cached output instead of reading the file
        if not force:
            if payload == self._cached_output:
                return self

            cached_normalized = self._without_volatile_fields(self._cached_output)
            payload_normalized = self._without_volatile_fields(payload)
            if payload_normalized == cached_normalized:
                return self

        path.parent.mkdir(parents=True, exist_ok=True)
        initialize_task_data(path.parent.parent)
        atomic_write_toml(path, payload)

        # Update the cached output after saving
        self._cached_output = payload
        return self
