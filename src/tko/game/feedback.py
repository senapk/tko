from tko.game.task import Task
from tko.repository.repository import Repository
from pathlib import Path
# import toml library


FEEDBACK_TOML = r'''
[[perguntas]]
tag = "what"
pergunta = "O quanto da atividade foi realizada?"
resposta = ""

[[perguntas]]
tag = "how"
pergunta = "Com quem e como você realizou a atividade?"
resposta = ""

[[perguntas]]
tag = "tools"
pergunta = """
Quais ferramentas ou recursos você utilizou para realizar a atividade?
Informe se utilizou IA generativa e, em caso afirmativo, como ela foi utilizada 
(pesquisar, estudar, gerar ideias, escrever, gerar código, revisar ou depurar).
"""
resposta = """
"""

[[perguntas]]
tag = "learned"
pergunta = "O que você aprendeu e quais elementos ainda precisam de maior estudo?"
resposta = ""
'''

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

    # def check_feedback_wrote(self) -> bool:
    #     # parse toml fila and search for empty answers
    #     feedback_path = self.get_feedback_toml_path()
    #     if feedback_path is None or not feedback_path.exists():
    #         return False
    #     content = feedback_path.read_text()