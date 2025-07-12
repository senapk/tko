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

    def __init__(self):
        self.rate: int = 0
        self.flow: int = 0
        self.edge: int = 0
        self.neat: int = 0
        self.cool: int = 0
        self.easy: int = 0
    
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

    def get_kv(self) -> dict[str, str]:
        kv: dict[str, str] = {TaskInfo.rate_str: str(self.rate), TaskInfo.flow_str: str(self.flow),
                              TaskInfo.edge_str: str(self.edge), TaskInfo.neat_str: str(self.neat),
                              TaskInfo.cool_str: str(self.cool), TaskInfo.easy_str: str(self.easy)}
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

        return kv
    
    