from .task_info import TaskInfo
import numpy as np

class TaskGrader:
    def __init__(self, task_info: TaskInfo):
        self.info = task_info

    @staticmethod
    def get_harmonic_mean(a: float, b: float, c: float) -> float:
        if a == 0 or b == 0 or c == 0:
            return 0.0
        return 3 / (1.0 / a + 1.0 / b + 1.0 / c)

    @staticmethod
    def get_square_mean(a: float, b: float, c: float) -> float:
        if a == 0 or b == 0 or c == 0:
            return 0.0
        return ((a * b * c) ** 0.5) / 10.0
    
    @staticmethod
    def get_cubic_square(a: float, b: float, c: float) -> float:
        if a == 0 or b == 0 or c == 0:
            return 0.0
        return ((a * b * c) ** (1/3))

    @staticmethod
    def get_product(a: float, b: float, c: float) -> float:
        if a == 0 or b == 0 or c == 0:
            return 0.0
        return (a * b * c) / 10000
    
    @staticmethod
    def get_sigmoid(a: float, b: float, c: float) -> float:
        x = a * b * c / 1000.0
        k = 0.011  # steepness of the curve
        x0 = 500.0
        v = 1 / (1 + np.exp(-k * (x - x0))) #numpy sigmoid function
        # v = 1 / (1 + (2.71828 ** (-k * (x - x0))))  # using e constant directly for compatibility
        return v * 100.0



    def get_percent(self):
        # hardcoded gambi for compatibility
        rate = float(self.info.rate)
        alone = float(self.info.alone) * 10
        # return Task.get_square_mean(flow, edge, rate)
        # return Task.get_harmonic_mean(flow, edge, rate)
        # return Task.get_cubic_square(flow, edge, rate)
        return TaskGrader.get_product(rate, alone, 100) 


    def get_ratio(self) -> float:
        return self.get_percent() / 100.0
