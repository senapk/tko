from tko.game.task import Task
from tko.repository.repository import Repository
from pathlib import Path


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
    
    # This method checks if the feedback has been filled out by the user. It returns True if any of the required fields have been filled, and False otherwise.
    def get_feedback_status(self) -> tuple[FeedbackStatus, int]:
            tags = ["what", "how", "tools", "learned"]
            total_tags = len(tags)
            
            feedback_path = self.get_feedback_toml_path()
            if feedback_path is None or not feedback_path.exists():
                return FeedbackStatus.NOT_FILLED, total_tags
                
            import tomllib
            try:
                with feedback_path.open("rb") as f:
                    data = tomllib.load(f)
                for p in tags:
                    if p not in data or not isinstance(data[p], str):
                        return FeedbackStatus.INVALID, total_tags
                        
                count_filled = sum(1 for p in tags if data[p].strip() != "")
                
                if count_filled == 0:
                    return FeedbackStatus.NOT_FILLED, total_tags
                elif count_filled < total_tags:
                    return FeedbackStatus.MISSING_FIELDS, total_tags - count_filled
                else:
                    return FeedbackStatus.FILLED, 0
                    
            except tomllib.TOMLDecodeError:
                # Pegando especificamente erros de sintaxe (ex: aluno apagou aspas)
                return FeedbackStatus.INVALID, total_tags
            except Exception:    
                # Catch-all de segurança
                return FeedbackStatus.INVALID, total_tags
