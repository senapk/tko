from __future__ import annotations
import yaml # type: ignore
from pathlib import Path
from typing import Any
from tko.util.decoder import Decoder
from tko.util.rtext import RText
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
                    f"Git merge conflict detected in {self.repo.paths.config_file}.\n"
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
                raise FileNotFoundError(f"Arquivo de configuração vazio: {self.repo.paths.config_file}")
                
        except ConfigMergeConflictError:
            raise
        except yaml.YAMLError as e:
            raise Warning(RText.parse(f"O arquivo de configuração do repositório [y]{self.repo.paths.config_file}[.] contém erros de YAML e está [r]corrompido[.].\nErro: {e}\nAbra e corrija o conteúdo ou crie um novo."))
        except FileNotFoundError:
            raise Warning(RText.parse(f"O arquivo de configuração do repositório [y]{self.repo.paths.config_file}[.] está [r]vazio[.].\nAbra e corrija o conteúdo ou crie um novo."))
        except Exception as e:
            raise Warning(RText.parse(f"O arquivo de configuração do repositório [y]{self.repo.paths.config_file}[.] está [r]corrompido[.].\nErro inesperado: {e}\nAbra e corrija o conteúdo ou crie um novo."))

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
