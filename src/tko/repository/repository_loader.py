from __future__ import annotations
import yaml # type: ignore
from pathlib import Path
from typing import Any
from tko.util.decoder import Decoder
from tko.util.text import Text
from tko.util.atomic_write_yaml import atomic_write_yaml
from tko.repository.repository import Repository

class ConfigMergeConflictError(Exception):
    pass

class RepositoryLoader:
    def __init__(self, repo: Repository): # repo is of type Repository
        self.repo = repo

    def check_for_merge_conflicts(self, content: str):
        lines = content.splitlines()
        for line in lines:
            if line.startswith("<<<<<<<") or line.startswith("=======") or line.startswith(">>>>>>>"):
                raise ConfigMergeConflictError(
                    f"Git merge conflict detected in {self.repo.paths.get_config_file()}.\n"
                    "Please resolve the conflict manually before continuing."
                )
    @staticmethod
    def length(data: Any) -> int:
        if isinstance(data, dict):
            return len(data) # type: ignore
        elif isinstance(data, list):
            return len(data) # type: ignore
        else:
            return 0

    def load_config(self) -> RepositoryLoader:
        content = Decoder.load(self.repo.paths.get_config_file())
        self.check_for_merge_conflicts(content)
        
        local_data: dict[str, Any] | Any = {}
        try:
            local_data = yaml.safe_load(content)
            if local_data is None or not isinstance(local_data, dict) or self.length(local_data) == 0:
                backup_content = Decoder.load(self.repo.paths.get_config_backup_file())
                self.check_for_merge_conflicts(backup_content)
                local_data = yaml.safe_load(backup_content)
                
            if local_data is None or not isinstance(local_data, dict) or self.length(local_data) == 0:
                raise FileNotFoundError(f"Arquivo de configuração vazio: {self.repo.paths.get_config_file()}")
                
        except ConfigMergeConflictError:
            raise
        except yaml.YAMLError as e:
            raise Warning(Text.format(f"O arquivo de configuração do repositório {{y}} contém erros de YAML e está {{r}}.\nErro: {e}\nAbra e corrija o conteúdo ou crie um novo.", self.repo.paths.get_config_file(), "corrompido"))
        except FileNotFoundError:
            raise Warning(Text.format("O arquivo de configuração do repositório {y} está {r}.\nAbra e corrija o conteúdo ou crie um novo.", self.repo.paths.get_config_file(), "vazio"))
        except Exception as e:
            raise Warning(Text.format(f"O arquivo de configuração do repositório {{y}} está {{r}}.\nErro inesperado: {e}\nAbra e corrija o conteúdo ou crie um novo.", self.repo.paths.get_config_file(), "corrompido"))

        self.repo.data.load_from_dict(local_data) # type: ignore
        self.repo.flags.from_dict(self.repo.data.flags) # type: ignore
        
        for source in self.repo.data.get_sources():
            source.set_source_globals(self.repo.paths.get_repo_root_dir(), self.repo.paths.get_cache_folder())

        return self

    def save_config(self) -> RepositoryLoader:
        self.repo.data.version = "0.2"
        self.repo.data.flags = self.repo.flags.to_dict()
        path: Path = Path(self.repo.paths.get_config_file())
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_yaml(path, self.repo.data.save_to_dict())
        return self
