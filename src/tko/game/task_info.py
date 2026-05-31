from __future__ import annotations


class TaskSelfInfo:
    class Key:
        RATE: str = "rate"

        IA_CONCEPT: str = "concept"
        IA_PROBLEM: str = "problem"
        IA_CODING: str = "code"
        IA_DEBUG: str = "debug"
        IA_REFACTOR: str = "refactor"
        
        GUIDED: str = "guided" # se fez a atividade seguindo a aula presencial ou vídeo aula
        FRIEND: str = "friend" # friend name
        STUDY_TIME: str = "study" # study time spent in minutes
        FEEDBACK: str = "self" # feedback done for the task

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
        return TaskSelfInfo().from_kv(self.get_kv())

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

 
    def from_kv(self, kv: dict[str, str]):
        if self.Key.RATE in kv:
            self.set_rate(kv[self.Key.RATE])
        if self.Key.STUDY_TIME in kv:
            self.set_study(kv[self.Key.STUDY_TIME])
        self.friend = kv.get(self.Key.FRIEND, "")
        self.feedback = kv.get(self.Key.FEEDBACK, "0") == "1"
        self.guided = kv.get(self.Key.GUIDED, "0") == "1"
        self.ia_concept = kv.get(self.Key.IA_CONCEPT, "0") == "1"
        self.ia_problem = kv.get(self.Key.IA_PROBLEM, "0") == "1"
        self.ia_code = kv.get(self.Key.IA_CODING, "0") == "1"
        self.ia_debug = kv.get(self.Key.IA_DEBUG, "0") == "1"
        self.ia_refactor = kv.get(self.Key.IA_REFACTOR, "0") == "1"
        return self

    def get_kv(self) -> dict[str, str]:
        kv: dict[str, str] = {}
        if self.feedback:
            kv[self.Key.FEEDBACK] = "1"
        if self.rate != 0:
            kv[self.Key.RATE] = str(self.rate)
        if self.study != 0:
            kv[self.Key.STUDY_TIME] = str(self.study)
        if self.friend:
            kv[self.Key.FRIEND] = self.friend
        if self.guided:
            kv[self.Key.GUIDED] = "1"
        if self.ia_concept:
            kv[self.Key.IA_CONCEPT] = "1"
        if self.ia_problem:
            kv[self.Key.IA_PROBLEM] = "1"
        if self.ia_code:
            kv[self.Key.IA_CODING] = "1"
        if self.ia_debug:
            kv[self.Key.IA_DEBUG] = "1"
        if self.ia_refactor:
            kv[self.Key.IA_REFACTOR] = "1"
        return kv
    
    