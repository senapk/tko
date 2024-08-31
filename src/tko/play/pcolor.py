class PColor:
    @staticmethod
    def focus():
        return "B"
    
    @staticmethod
    def prog_done():
        return "g"
    @staticmethod
    def prog_todo():
        return "y"
    @staticmethod
    def flag_on():
        return "G"
    @staticmethod
    def flag_off():
        return "Y"

    @staticmethod
    def skill_done():
        return "C"
    @staticmethod
    def skill_todo():
        return "M"
    @staticmethod
    def main_done():
        return "G"
    @staticmethod
    def main_todo():
        return "R"    
    @staticmethod
    def skills():
        return "c"

    @staticmethod
    def new():
        return "g"

    nothing = "m"
    started = "r"
    required = "y"
    complete = "g"

    shell = "r"
    htext = ""
    check = "g"
    uncheck = "y"
    param = "c"
