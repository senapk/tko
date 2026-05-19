from __future__ import annotations
import yaml # type: ignore
from pathlib import Path
from typing import Any
from tko.util.decoder import Decoder
from tko.i18n import Msg, t
from tko.util.rt import RT
from tko.util.atomic_write_yaml import atomic_write_yaml
from tko.repository.repository import Repository


_REPOSITORY_LOADER_GIT_CONFLICT = Msg(
    pt="Conflito de merge git detectado em {file}.\nResolva o conflito manualmente antes de continuar.",
    en="Git merge conflict detected in {file}.\nPlease resolve the conflict manually before continuing.",
)
_REPOSITORY_LOADER_EMPTY_CONFIG_FILE = Msg(
    pt="Arquivo de configuração vazio: {file}",
    en="Empty config file: {file}",
)
_REPOSITORY_LOADER_YAML_CORRUPTED = Msg(
    pt="O arquivo de configuração do repositório <{file}:y> contém erros de YAML e está <corrompido:r>.\nErro: {error}\nAbra e corrija o conteúdo ou crie um novo.",
    en="The repository configuration file <{file}:y> contains YAML errors and is <corrupted:r>.\nError: {error}\nOpen and fix the content or create a new one.",
)
_REPOSITORY_LOADER_CONFIG_EMPTY = Msg(
    pt="O arquivo de configuração do repositório <{file}:y> está <vazio:r>.\nAbra e corrija o conteúdo ou crie um novo.",
    en="The repository configuration file <{file}:y> is <empty:r>.\nOpen and fix the content or create a new one.",
)
_REPOSITORY_LOADER_CONFIG_CORRUPTED_UNEXPECTED = Msg(
    pt="O arquivo de configuração do repositório <{file}:y> está <corrompido:r>.\nErro inesperado: {error}\nAbra e corrija o conteúdo ou crie um novo.",
    en="The repository configuration file <{file}:y> is <corrupted:r>.\nUnexpected error: {error}\nOpen and fix the content or create a new one.",
)

class ConfigMergeConflictError(Exception):
    pass

class RepositoryLoader:
    def __init__(self, repo: Repository): # repo is of type Repository
        self.repo = repo

    def check_for_merge_conflicts(self, content: str):
        lines = content.splitlines()
        for line in lines:
            if line.startswith("<<<<<<<") or line.startswith("=======") or line.startswith(">>>>>>>"):
                raise ConfigMergeConflictError(t(_REPOSITORY_LOADER_GIT_CONFLICT, file=self.repo.paths.config_file))
    @staticmethod
    def length(data: Any) -> int:
        if isinstance(data, dict):
            return len(data) # type: ignore
        elif isinstance(data, list):
            return len(data) # type: ignore
        else:
            return 0

    def load_config(self) -> RepositoryLoader:
        content = Decoder.load(self.repo.paths.config_file)
        self.check_for_merge_conflicts(content)
        
        local_data: dict[str, Any] | Any = {}
        try:
            local_data = yaml.safe_load(content)
            if local_data is None or not isinstance(local_data, dict) or self.length(local_data) == 0:
                backup_content = Decoder.load(self.repo.paths.config_backup_file)
                self.check_for_merge_conflicts(backup_content)
                local_data = yaml.safe_load(backup_content)
                
            if local_data is None or not isinstance(local_data, dict) or self.length(local_data) == 0:
                raise FileNotFoundError(t(_REPOSITORY_LOADER_EMPTY_CONFIG_FILE, file=self.repo.paths.config_file))
                
        except ConfigMergeConflictError:
            raise
        except yaml.YAMLError as e:
            raise Warning(RT.parse(t(_REPOSITORY_LOADER_YAML_CORRUPTED, file=self.repo.paths.config_file, error=e)))
        except FileNotFoundError:
            raise Warning(RT.parse(t(_REPOSITORY_LOADER_CONFIG_EMPTY, file=self.repo.paths.config_file)))
        except Exception as e:
            raise Warning(RT.parse(t(_REPOSITORY_LOADER_CONFIG_CORRUPTED_UNEXPECTED, file=self.repo.paths.config_file, error=e)))

        self.repo.data.load_from_dict(local_data) # type: ignore
        self.repo.flags.from_dict(self.repo.data.flags) # type: ignore
        
        return self

    def save_config(self) -> RepositoryLoader:
        self.repo.data.version = "0.2"
        self.repo.data.flags = self.repo.flags.to_dict()
        path: Path = Path(self.repo.paths.config_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_yaml(path, self.repo.data.save_to_dict())
        return self
