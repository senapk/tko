class TaskBasic:
    def __init__(self, key: str = ""):
        self.key = key
        self.coverage = 0
        self.autonomy = 0
        self.skill = 0
        self.timestamp: str = ""

    def set_coverage(self, value: int):
        if value >= 0:
            self.coverage = value
        return self

    def set_autonomy(self, value: int):
        if value >= 0:
            self.autonomy = value
        return self
    
    def set_skill(self, value: int):
        if value >= 0:
            self.skill = value
        return self

    def set_timestamp(self, timestamp: str):
        self.timestamp = timestamp
        return self

    def __eq__(self, other):
        if not isinstance(other, TaskBasic):
            return False
        dr: TaskBasic = other
        return self.coverage == dr.coverage and self.autonomy == dr.autonomy and self.skill == dr.skill

    def __str__(self):
        return "{" + f'k:{self.key}, c:{self.coverage}, a:{self.autonomy}, s:{self.skill}' + "}"