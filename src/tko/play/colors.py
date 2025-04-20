class Colors:
    def __init__(self):
        self.focused_item: str = "B"
        self.task_text_done: str = "g"
        self.task_text_todo: str = "y"
        self.button_flag_on: str = "G"
        self.button_flag_off: str = "Y"
        self.progress_skill_done: str = "C"
        self.progress_skill_todo: str = "M"
        self.main_bar_done: str = "G"
        self.main_bar_todo: str = "R"
        self.task_skills: str = "c"
        self.task_new: str = "g"
        self.mark_nothing: str = "m"
        self.mark_started: str = "r"
        self.mark_required: str = "y"
        self.mark_complete: str = "g"
    
    def to_dict(self):
        return self.__dict__
    
    def from_dict(self, attr_dict: dict[str, str]):
        for key, value in attr_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
