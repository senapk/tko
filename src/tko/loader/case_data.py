class CaseData:
    def __init__(self, case: str="", inp: str="", outp: str="", grade: None | int = None):
        self.case: str = case
        self.input: str = CaseData.finish(inp)
        self.output: str = CaseData.unwrap(CaseData.finish(outp))
        self.grade: None | int = grade

    @staticmethod
    def finish(text: str):
        return text if text.endswith("\n") else text + "\n"

    @staticmethod
    def unwrap(text: str):
        while text.endswith("\n"):
            text = text[:-1]
        if text.startswith("\"") and text.endswith("\""):
            text = text[1:-1]
        return CaseData.finish(text)

    # @override
    def __str__(self) -> str:
        return "case=" + self.case + '\n' \
                + "input=" + self.input \
                + "output=" + self.output \
                + "gr=" + str(self.grade)