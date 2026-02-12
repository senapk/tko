class TaskInfo:
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

    def clone(self):
        return TaskInfo().load_from_kv(self.get_kv())

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
        if TaskInfo.Keys.rate_str in kv:
            self.set_rate(kv[TaskInfo.Keys.rate_str])
        if TaskInfo.Keys.study_str in kv:
            self.set_study(kv[TaskInfo.Keys.study_str])
        self.friend = kv.get(TaskInfo.Keys.friend_str, "")
        self.feedback = kv.get(TaskInfo.Keys.feedback_str, "0") == "1"
        self.guided = kv.get(TaskInfo.Keys.guided_str, "0") == "1"
        self.ia_concept = kv.get(TaskInfo.Keys.ia_concept_str, "0") == "1"
        self.ia_problem = kv.get(TaskInfo.Keys.ia_problem_str, "0") == "1"
        self.ia_code = kv.get(TaskInfo.Keys.ia_coding_str, "0") == "1"
        self.ia_debug = kv.get(TaskInfo.Keys.ia_debug_str, "0") == "1"
        self.ia_refactor = kv.get(TaskInfo.Keys.ia_refactor_str, "0") == "1"
        return self

    def get_kv(self) -> dict[str, str]:
        kv: dict[str, str] = {}
        kv[TaskInfo.Keys.feedback_str] = "1" if self.feedback else "0"
        if self.rate != 0:
            kv[TaskInfo.Keys.rate_str] = str(self.rate)
        if self.study != 0:
            kv[TaskInfo.Keys.study_str] = str(self.study)
        if self.friend:
            kv[TaskInfo.Keys.friend_str] = self.friend
        if self.guided:
            kv[TaskInfo.Keys.guided_str] = "1"
        if self.ia_concept:
            kv[TaskInfo.Keys.ia_concept_str] = "1"
        if self.ia_problem:
            kv[TaskInfo.Keys.ia_problem_str] = "1"
        if self.ia_code:
            kv[TaskInfo.Keys.ia_coding_str] = "1"
        if self.ia_debug:
            kv[TaskInfo.Keys.ia_debug_str] = "1"
        if self.ia_refactor:
            kv[TaskInfo.Keys.ia_refactor_str] = "1"

        return kv
    
    