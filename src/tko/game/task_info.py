from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class TaskSelfInfo:
    class Key:
        RATE: str = "rate"
        BOSS: str = "boss" # Feito no modo de avaliação
        STUDY_TIME: str = "study" # study time spent in minutes
        FEEDBACK: str = "self" # feedback done for the task

    rate: int = 0
    study: int = 0  # Quantos minutos ele estudou para fazer a atividade
    boss: bool = False  # Feito no modo de avaliação
    feedback: bool = False # Se fez a auto avaliação
    
    def copy_quality_from(self, other: TaskSelfInfo):
        self.feedback = other.feedback
        self.boss = other.boss

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
        if self.Key.BOSS in kv:
            self.boss = kv.get(self.Key.BOSS, "0") == "1"
        self.feedback = kv.get(self.Key.FEEDBACK, "0") == "1"
        

        return self

    def get_kv(self, full: bool = False) -> dict[str, str]:
        kv: dict[str, str] = {}
        if full or self.feedback:
            kv[self.Key.FEEDBACK] = "1" if self.feedback else "0"
        if full or self.rate != 0:
            kv[self.Key.RATE] = str(self.rate)
        if full or self.study != 0:
            kv[self.Key.STUDY_TIME] = str(self.study)
        if full or self.boss:
            kv[self.Key.BOSS] = "1" if self.boss else "0"
        return kv
    
    