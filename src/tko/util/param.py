from typing import Optional
from .consts import DiffCount, DiffMode

class Param:

    def __init__(self):
        pass

    class Basic:
        def __init__(self):
            self.index: Optional[int] = None
            self.label_pattern: Optional[str] = None
            self.diff_mode = DiffMode.SIDE
            self.diff_count = DiffCount.FIRST
            self.filter: bool = False
            self.compact: bool = False

        def set_index(self, value: Optional[int]):
            self.index= value
            return self

        def set_label_pattern(self, label_pattern: Optional[str]):
            self.label_pattern = label_pattern
            return self
        
        def set_compact(self, value: bool):
            self.compact = value
            return self

        def set_diff_mode(self, value: DiffMode):
            self.diff_mode = value
            return self
    
        def set_filter(self, value: bool):
            self.filter = value
            return self

        def set_diff_count(self, value: DiffCount):
            self.diff_count = value
            return self

    class Manip:
        def __init__(self):
            self.unlabel: bool = False
            self.to_sort: bool = False
            self.to_number: bool = False
        
        def set_unlabel(self, value: bool):
            self.unlabel = value
            return self
        
        def set_to_sort(self, value: bool):
            self.to_sort = value
            return self
        
        def set_to_number(self, value: bool):
            self.to_number = value
            return self
