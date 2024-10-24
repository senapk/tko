import json
import os

class TaskData:
    def __init__(self, key: str = "", progress: int = 0, seft_grade: int = 0):
        self.key = key
        self.progress = progress
        self.seft_grade = seft_grade

    def decode(self, serial: str):
        key, progress, seft_grade = serial.split(":")
        self.key = key
        self.progress = int(progress)
        self.seft_grade = int(seft_grade)

    def __eq__(self, other):
        return self.progress == other.progress and self.seft_grade == other.seft_grade


    def __str__(self):
        return f'{self.key}:{self.progress}:{self.seft_grade}'
    

    
class DailyLog:
    def __init__(self, json_file: str):
        # dict[day, dict[task_key, TaskLog]]
        self.history: dict[str, dict[str, TaskData]] = {}
        self.json_file = json_file
        self.load_json()

        self.resume: dict[str, TaskData] = {}
        self.generate_resume()

    def load_json(self):
        history = {}
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r') as f:
                    history = json.load(f)
        except:
            pass

        self.history = {}
        for day, serial_list in history.items():
            self.history[day] = {}
            for serial in serial_list:
                task_data = TaskData()
                task_data.decode(serial)
                self.history[day][task_data.key] = task_data

    def generate_resume(self):
        self.resume = {}
        #sort by tasklogrep by day
        for day in sorted(self.history.keys()):
            for task_key, task_log in self.history[day].items():
                self.resume[task_key] = task_log

    # def match_actual_state(self, day: str, actual_state: dict[str, TaskData]):
    #     if day not in self.history:
    #         self.history[day] = {}
    #     changed = False
    #     for _, task_data in actual_state.items():
    #         if self.__check_add_task(day, task_data):
    #                 changed = True
        
    #     if changed:
    #         self.save()

    def __check_add_task(self, day: str, task_data: TaskData) -> bool:
        data = self.resume.get(task_data.key, None)

        # não tinha, e ainda está zerado, não precisa salvar
        if data is None and task_data.progress == 0 and task_data.seft_grade == 0:
            return False
        
        # tinha, e está diferente, precisa salvar
        if data is None or data != task_data:
            if day not in self.history:
                self.history[day] = {}
            self.history[day][task_data.key] = task_data
            self.resume[task_data.key] = task_data
            return True
        return False
    
    def log_task(self, day: str, key: str, progress: int = -1, self_grade: int = -1, save_on_change: bool = True):
        actual_progress = self.resume.get(key, TaskData(key, 0, 0)).progress
        actual_seft_grade = self.resume.get(key, TaskData(key, 0, 0)).seft_grade
        if progress == -1:
            progress = actual_progress
        if self_grade == -1:
            self_grade = actual_seft_grade
        if self.__check_add_task(day, TaskData(key, progress, self_grade)):
            if save_on_change:
                self.save()
            return True
        return False

    def save(self):
        history = {}
        for day, task_data in self.history.items():
            history[day] = [str(task) for task in task_data.values()]
        with open(self.json_file, 'w') as f:
            json.dump(history, f, indent=4)
