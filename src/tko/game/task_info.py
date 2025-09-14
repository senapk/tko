class TaskInfo:
    rate_max: int = 100
    flow_max: int = 6
    edge_max: int = 5
    neat_max: int = 5
    cool_max: int = 5
    easy_max: int = 5


    rate_str: str = "rate"
    flow_str: str = "flow"
    edge_str: str = "edge"
    neat_str: str = "neat"
    cool_str: str = "cool"
    easy_str: str = "easy"

    alone_max = 10
    alone_str: str = "alone" # doing alone, no help
    human_str: str = "human" # using human help: friend or monitor
    iagen_str: str = "iagen" # using AI generation: gpt-4, dalle-3
    guide_str: str = "guide" # using guide: tutorial, doc, class, youtube
    other_str: str = "other" # using other help: book, search, forum
    study_str: str = "study" # study time spent in minutes

    def __init__(self):
        self.rate: int = 0

        self.flow: int = 0 # deprecated
        self.edge: int = 0 # deprecated
        self.neat: int = 0 # deprecated
        self.cool: int = 0 # deprecated
        self.easy: int = 0 # deprecated

        self.alone: int = 0
        self.human: str = ""
        self.iagen: str = ""
        self.guide: str = ""
        self.other: str = ""
        self.study: int = 0

    def set_study(self, value: int):
        if value >= 0:
            self.study = value
            return self
        else:
            raise ValueError(f"Invalid study minutes:{value}")

    def get_study(self) -> int:
        return self.study

    def set_human(self, value: str):
        self.human = value
        return self
    
    def set_iagen(self, value: str):
        self.iagen = value
        return self
    
    def set_guide(self, value: str):
        self.guide = value
        return self
    
    def set_other(self, value: str):
        self.other = value
        return self
    
    def set_alone(self, value: int):
        if 0 <= value <= TaskInfo.alone_max:
            self.alone = value
            return self
        else:
            raise ValueError(f"Invalid {TaskInfo.alone_str}:{value}")

    def set_rate(self, value: int):
        if 0 <= value <= TaskInfo.rate_max:
            self.rate = value
            return self
        else:
            raise ValueError(f"Invalid {TaskInfo.rate_str}:{value}")
    
    def set_flow(self, value: int):
        if 0 <= value <= TaskInfo.flow_max:
            self.flow = value
            return self
        else:
            raise ValueError(f"Invalid {TaskInfo.flow_str}:{value}")

    def set_edge(self, value: int):
        if 0 <= value <= TaskInfo.edge_max:
            self.edge = value
            return self
        else:
            raise ValueError(f"Invalid {TaskInfo.edge_str}:{value}")

    def set_neat(self, value: int):
        if 0 <= value <= TaskInfo.neat_max:
            self.neat = value
            return self
        else:
            raise ValueError(f"Invalid {TaskInfo.neat_str}:{value}")
        
    def set_cool(self, value: int):
        if 0 <= value <= TaskInfo.cool_max:
            self.cool = value
            return self
        else:
            raise ValueError(f"Invalid {TaskInfo.cool_str}:{value}")

    def set_easy(self, value: int):
        if 0 <= value <= TaskInfo.easy_max:
            self.easy = value
            return self
        else:
            raise ValueError(f"Invalid {TaskInfo.easy_str}:{value}")
        
    def get_rate(self) -> int:
        return self.rate
    def get_flow(self) -> int:
        return self.flow
    def get_edge(self) -> int:
        return self.edge
    def get_neat(self) -> int:
        return self.neat
    def get_cool(self) -> int:
        return self.cool
    def get_easy(self) -> int:
        return self.easy
    
    def get_human(self) -> str:
        return self.human
    def get_iagen(self) -> str:
        return self.iagen
    def get_guide(self) -> str:
        return self.guide
    def get_other(self) -> str:
        return self.other
    def get_alone(self) -> int:
        return self.alone
    

    def load_from_kv(self, kv: dict[str, str]):
        if TaskInfo.rate_str in kv:
            self.rate = int(kv[TaskInfo.rate_str])
        if TaskInfo.flow_str in kv:
            self.flow = int(kv[TaskInfo.flow_str])
        if TaskInfo.edge_str in kv:
            self.edge = int(kv[TaskInfo.edge_str])
        if TaskInfo.neat_str in kv:
            self.neat = int(kv[TaskInfo.neat_str])
        if TaskInfo.cool_str in kv:
            self.cool = int(kv[TaskInfo.cool_str])
        if TaskInfo.easy_str in kv:
            self.easy = int(kv[TaskInfo.easy_str])
        if TaskInfo.human_str in kv:
            self.human = kv[TaskInfo.human_str]
        if TaskInfo.iagen_str in kv:
            self.iagen = kv[TaskInfo.iagen_str]
        if TaskInfo.guide_str in kv:
            self.guide = kv[TaskInfo.guide_str]
        if TaskInfo.other_str in kv:
            self.other = kv[TaskInfo.other_str]
        if TaskInfo.alone_str in kv:
            self.alone = int(kv[TaskInfo.alone_str])
        if TaskInfo.study_str in kv:
            self.study = int(kv[TaskInfo.study_str])
        return self

    def get_kv(self) -> dict[str, str]:
        kv: dict[str, str] = {TaskInfo.rate_str: str(self.rate), 
                              TaskInfo.flow_str: str(self.flow),
                              TaskInfo.edge_str: str(self.edge), 
                              TaskInfo.neat_str: str(self.neat),
                              TaskInfo.cool_str: str(self.cool), 
                              TaskInfo.easy_str: str(self.easy),
                              TaskInfo.human_str: self.human,
                              TaskInfo.iagen_str: self.iagen,
                              TaskInfo.guide_str: self.guide, 
                              TaskInfo.other_str: self.other,
                              TaskInfo.alone_str: str(self.alone), 
                              TaskInfo.study_str: str(self.study)}
        return kv
    
    def get_filled_kv(self) -> dict[str, str]:
        kv: dict[str, str] = {}
        if self.rate > 0:
            kv[TaskInfo.rate_str] = str(self.rate)
        if self.flow > 0:
            kv[TaskInfo.flow_str] = str(self.flow)
        if self.edge > 0:
            kv[TaskInfo.edge_str] = str(self.edge)
        if self.neat > 0:
            kv[TaskInfo.neat_str] = str(self.neat)
        if self.cool > 0:
            kv[TaskInfo.cool_str] = str(self.cool)
        if self.easy > 0:
            kv[TaskInfo.easy_str] = str(self.easy)
        if self.human:
            kv[TaskInfo.human_str] = self.human
        if self.iagen:
            kv[TaskInfo.iagen_str] = self.iagen
        if self.guide:       
            kv[TaskInfo.guide_str] = self.guide
        if self.other:
            kv[TaskInfo.other_str] = self.other
        if self.alone > 0:
            kv[TaskInfo.alone_str] = str(self.alone)
        if self.study > 0:
            kv[TaskInfo.study_str] = str(self.study)

        return kv
    
    