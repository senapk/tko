class Colors:
    def __init__(self):
        self.focused_item = "B"
        self.task_text_done = "g"
        self.task_text_todo = "y"
        self.button_flag_on = "G"
        self.button_flag_off = "Y"
        self.progress_skill_done = "C"
        self.progress_skill_todo = "M"
        self.main_bar_done = "G"
        self.main_bar_todo = "R"
        self.task_skills = "c"
        self.task_new = "g"
        self.mark_nothing = "m"
        self.mark_started = "r"
        self.mark_required = "y"
        self.mark_complete = "g"
    
    def to_dict(self):
        return self.__dict__
    
    def from_dict(self, attr_dict):
        for key, value in attr_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
