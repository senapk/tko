import json
import tomllib
from pathlib import Path

from tko.game.task import Task
from tko.repository.repository import Repository


FEEDBACK_TOML = r'''# O que/quanto da atividade foi realizada?
what = ""

# Com quem e/ou como você realizou a atividade?
how = ""

# Quais ferramentas ou recursos você utilizou para realizar a atividade?
# Informe se utilizou IA generativa e, em caso afirmativo, como ela foi utilizada 
# (pesquisar, estudar, gerar ideias, escrever, gerar código, revisar ou depurar).
tools = """
"""

# O que você aprendeu e quais elementos ainda precisam de maior estudo?
learned = ""
'''


import enum


class FeedbackStatus(enum.Enum):
    NOT_FILLED = 0
    FILLED = 1
    MISSING_FIELDS = 2
    INVALID = 3

class Feedback:
    FIELDS = ("what", "how", "tools", "learned")

    def __init__(self, repo: Repository, task: Task):
        self.repo: Repository = repo
        self.task: Task = task

    def get_feedback_toml_path(self) -> Path | None:
        path = self.repo.task_resolver.target_folder(self.task)
        if path is None:
            return None
        return path / "src" / "feedback.toml"

    def ensure_feedback_file(self) -> bool:
        feedback_path = self.get_feedback_toml_path()
        if feedback_path is None:
            return False
        feedback_path.parent.mkdir(parents=True, exist_ok=True)
        if not feedback_path.exists():
            feedback_path.write_text(FEEDBACK_TOML)
        return True

    def reset_feedback_file(self) -> bool:
        feedback_path = self.get_feedback_toml_path()
        if feedback_path is None:
            return False
        feedback_path.parent.mkdir(parents=True, exist_ok=True)
        feedback_path.write_text(FEEDBACK_TOML)
        return True

    def load_fields(self) -> dict[str, str]:
        """Load the four managed feedback fields, rejecting malformed TOML."""
        feedback_path = self.get_feedback_toml_path()
        if feedback_path is None:
            raise ValueError("A tarefa não possui pasta local para o feedback.")
        if not feedback_path.exists():
            return {field: "" for field in self.FIELDS}
        try:
            with feedback_path.open("rb") as file:
                data = tomllib.load(file)
        except tomllib.TOMLDecodeError as error:
            raise ValueError("O arquivo de feedback possui TOML inválido.") from error
        except OSError as error:
            raise ValueError("Não foi possível ler o arquivo de feedback.") from error
        fields: dict[str, str] = {}
        for field in self.FIELDS:
            value = data.get(field, "")
            if not isinstance(value, str):
                raise ValueError("O arquivo de feedback possui campos inválidos.")
            fields[field] = value
        return fields

    def save_fields(self, fields: dict[str, str]) -> None:
        """Write the canonical feedback form managed by the Textual dialog."""
        feedback_path = self.get_feedback_toml_path()
        if feedback_path is None:
            raise ValueError("A tarefa não possui pasta local para o feedback.")
        values: dict[str, str] = {}
        for field in self.FIELDS:
            value = fields.get(field)
            if not isinstance(value, str):
                raise ValueError(f"Campo de feedback inválido: {field}.")
            values[field] = value
        feedback_path.parent.mkdir(parents=True, exist_ok=True)
        content = "\n".join(f"{field} = {json.dumps(values[field], ensure_ascii=False)}" for field in self.FIELDS)
        feedback_path.write_text(content + "\n", encoding="utf-8")

    def required_fields(self) -> tuple[str, ...]:
        """Return the feedback fields applicable to the task's saved evaluation."""
        info = getattr(self.task, "info", None)
        rate = getattr(info, "rate", 0)
        boss = getattr(info, "boss", False)
        fields: list[str] = []
        if rate < 100:
            fields.append("what")
        if not boss:
            fields.extend(("how", "tools"))
        fields.append("learned")
        return tuple(fields)
    
    def get_feedback_status(self) -> tuple[FeedbackStatus, int]:
        """Keep the legacy status contract for tree and history consumers."""
        required_fields = self.required_fields()
        total_fields = len(required_fields)
        feedback_path = self.get_feedback_toml_path()
        if feedback_path is None or not feedback_path.exists():
            return FeedbackStatus.NOT_FILLED, total_fields
        try:
            data = self.load_fields()
        except ValueError:
            return FeedbackStatus.INVALID, total_fields
        count_filled = sum(1 for field in required_fields if data[field].strip())
        if count_filled == 0:
            return FeedbackStatus.NOT_FILLED, total_fields
        if count_filled < total_fields:
            return FeedbackStatus.MISSING_FIELDS, total_fields - count_filled
        return FeedbackStatus.FILLED, 0
