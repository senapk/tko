from __future__ import annotations

class TaskSelfInfo:
    class Keys:
        rate_str: str = "rate"
        ia_concept_str: str = "concept"
        ia_problem_str: str = "problem"
        ia_coding_str: str = "code"
        ia_debug_str: str = "debug"
        ia_refactor_str: str = "refactor"
        guided_str: str = "guided"

        study_str: str = "study" # study time spent in minutes
        friend_str: str = "friend" #
        feedback_str: str = "self" # feedback for the task

    def __init__(self):
        self.rate: int = 0

        self.study: int = 0  # quantos minutos ele estudou para fazer a atividade

        self.feedback: bool = False # se fez a auto avaliação
        self.friend: str = "" # se usou ajuda de monitor, amigo, etc

        self.guided: bool = False # se fez a atividade seguindo a aula presencial ou vídeo aula        
        self.ia_concept: bool = False # se usou IA para entender o conceito
        self.ia_problem: bool = False # se usou IA para resolver o problema
        self.ia_code: bool = False # se usou IA para escrever código
        self.ia_debug: bool = False # se usou IA para debugar
        self.ia_refactor: bool = False # se usou IA para refatorar

    def copy_quality_from(self, other: TaskSelfInfo):
        self.feedback = other.feedback
        self.friend = other.friend
        
        self.guided = other.guided
        self.ia_concept = other.ia_concept
        self.ia_problem = other.ia_problem
        self.ia_code = other.ia_code
        self.ia_debug = other.ia_debug
        self.ia_refactor = other.ia_refactor


    def clone(self):
        return TaskSelfInfo().load_from_kv(self.get_kv())

    def set_study(self, value: str):
        try:
            minutes = int(value)
            if minutes >= 0:
                self.study = minutes
        except ValueError:
            self.study = 0
        return self
    
    def set_rate(self, value: str):
        try:
            rate = int(value)
            if 0 <= rate <= 100:
                self.rate = rate
        except ValueError:
            self.rate = 0
        return self

 
    def load_from_kv(self, kv: dict[str, str]):
        if TaskSelfInfo.Keys.rate_str in kv:
            self.set_rate(kv[TaskSelfInfo.Keys.rate_str])
        if TaskSelfInfo.Keys.study_str in kv:
            self.set_study(kv[TaskSelfInfo.Keys.study_str])
        self.friend = kv.get(TaskSelfInfo.Keys.friend_str, "")
        self.feedback = kv.get(TaskSelfInfo.Keys.feedback_str, "0") == "1"
        self.guided = kv.get(TaskSelfInfo.Keys.guided_str, "0") == "1"
        self.ia_concept = kv.get(TaskSelfInfo.Keys.ia_concept_str, "0") == "1"
        self.ia_problem = kv.get(TaskSelfInfo.Keys.ia_problem_str, "0") == "1"
        self.ia_code = kv.get(TaskSelfInfo.Keys.ia_coding_str, "0") == "1"
        self.ia_debug = kv.get(TaskSelfInfo.Keys.ia_debug_str, "0") == "1"
        self.ia_refactor = kv.get(TaskSelfInfo.Keys.ia_refactor_str, "0") == "1"
        return self

    def get_kv(self) -> dict[str, str]:
        kv: dict[str, str] = {}
        if self.feedback:
            kv[TaskSelfInfo.Keys.feedback_str] = "1"
        if self.rate != 0:
            kv[TaskSelfInfo.Keys.rate_str] = str(self.rate)
        if self.study != 0:
            kv[TaskSelfInfo.Keys.study_str] = str(self.study)
        if self.friend:
            kv[TaskSelfInfo.Keys.friend_str] = self.friend
        if self.guided:
            kv[TaskSelfInfo.Keys.guided_str] = "1"
        if self.ia_concept:
            kv[TaskSelfInfo.Keys.ia_concept_str] = "1"
        if self.ia_problem:
            kv[TaskSelfInfo.Keys.ia_problem_str] = "1"
        if self.ia_code:
            kv[TaskSelfInfo.Keys.ia_coding_str] = "1"
        if self.ia_debug:
            kv[TaskSelfInfo.Keys.ia_debug_str] = "1"
        if self.ia_refactor:
            kv[TaskSelfInfo.Keys.ia_refactor_str] = "1"
        return kv
    
    