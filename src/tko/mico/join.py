from __future__ import annotations

from collections.abc import Callable

from .class_task import ClassTask
from .collected import Collected, Game
from tko.logger.task_resume import TaskResume, Resume
from tko.cmds.cmd_rep import CmdRep
from tko.game.task_info import TaskInfo
from tko.game.quest_grader import QuestGrader
import subprocess

import re
import os
import json
from .csv_tools import CSV

def update_reference_rep(target: str) -> None:
    """Update the reference repository for the given target."""
    class_task = ClassTask(target).load_from_file()
    reference = class_task.get_reference_rep()
    if reference is None:
        raise ValueError("Reference directory is not set in the class task.")
    if not os.path.exists(reference):
        raise FileNotFoundError(f"Reference directory not found: {reference}")
    cmd = f"tko rep {reference} update"
    subprocess.run(cmd, shell=True, check=True)


def col_one_to_str(entry: Game.Task | Game.Quest) -> str:
    if isinstance(entry, Game.Task):
        opening = "*" if entry.opt else "+"
        return f'{opening}:{entry.value}:{entry.key}'
    else:
        opening = "="
        return f'{opening}:{entry.value}:{entry.key}'

def calc_quest_percent(quest: list[Game.Task], task_dict: dict[str, TaskResume]) -> float:
    """Calculate the percent of a quest based on its tasks."""
    if not quest:
        return 0.0
    elements: list[QuestGrader.Elem] = []
    for task in quest:
        elements.append(QuestGrader.Elem(
            value=task.value,
            opt=task.opt,
            percent=task_dict.get(task.key, TaskResume(task.key)).resume.percent
        ))
    earned_xp, total_xp = QuestGrader.calc_xp_earned_total(elements)
    percent = QuestGrader.get_percent(earned_xp, total_xp)
    return percent

def task_resume_to_str(task_resume: TaskResume) -> str:
    return f'{round(task_resume.resume.percent):03d}'

def task_resume_to_full_str(task_resume: TaskResume) -> str:
    """Convert a TaskResume to a string with detailed information."""
    resume: Resume = task_resume.resume
    info: TaskInfo = task_resume.info
    return f'{info.rate:03d}% {info.flow}{info.edge}how {resume.minutes:03d}m {resume.executions:03d}/{resume.versions:03d}ex {round(resume.percent):03d}%'

def quest_resume_to_str(tasks: list[Game.Task], user_task_dict: dict[str, TaskResume]) -> str:
    percent = calc_quest_percent(tasks, user_task_dict)
    return f'{round(percent):03d}'

def clear_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from a string."""
    ansi_escape = re.compile(r'\x1B\[[0-?9;]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


class Grid:
    def __init__(self, user_info_map: dict[str, Collected]):
        self.col_one: list[Game.Cluster] = []
        self.inside: dict[str, dict[str, str]] = {}
        self.user_label_task: dict[str, dict[str, TaskResume]] = {}
        for folder, info in user_info_map.items():
            self.user_label_task[folder] = info.resume
        self.row_one: list[str] = sorted(self.user_label_task.keys())
        self.col_one_to_str: Callable[[Game.Task | Game.Quest], str] = col_one_to_str
        self.task_resume_to_str: Callable[[TaskResume], str] = task_resume_to_str
        self.quest_resume_to_str: Callable[[list[Game.Task], dict[str, TaskResume]], str] = quest_resume_to_str
        self.include_tasks: bool = True  # Include tasks in the grid
        self.include_quests: bool = True  # Include quests in the grid


    def set_col_one_to_str_function(self, func: Callable[[Game.Task | Game.Quest], str]) -> Grid:
        self.col_one_to_str = func
        return self

    def set_task_resume_to_str_function(self, func: Callable[[TaskResume], str]) -> Grid:
        self.task_resume_to_str = func
        return self

    def set_quest_resume_to_str_function(self, func: Callable[[list[Game.Task], dict[str, TaskResume]], str]) -> Grid:
        self.quest_resume_to_str = func
        return self

    def __calc_student_entries(self, user: str) -> dict[str, str]:
        user_task_dict: dict[str, TaskResume] = self.user_label_task[user]
        output: dict[str, str] = {}
        for ref_cluster in self.col_one:
            for ref_quest in ref_cluster.quests:
                output[ref_quest.key] = self.quest_resume_to_str(ref_quest.tasks, user_task_dict)
                for task in ref_quest.tasks:
                    if task.key in user_task_dict:
                        output[task.key] = self.task_resume_to_str(user_task_dict[task.key])
        return output

    def set_reference(self, reference: Collected):
        self.col_one: list[Game.Cluster] = reference.clusters
        return self
    
    def set_include_tasks(self, include_tasks: bool) -> Grid:
        self.include_tasks = include_tasks
        return self

    def set_include_quests(self, include_quests: bool) -> Grid:
        self.include_quests = include_quests
        return self

    def build_csv(self) -> list[list[str]]:
        for user in self.row_one:
            self.inside[user] = self.__calc_student_entries(user)
    
        data: list[list[str]] = [['SIMPLE']]
        col_one_keys: list[str] = ['SIMPLE']
        # coluna 1
        for cluster in self.col_one:
            for quest in cluster.quests:
                if self.include_quests:
                    data.append([self.col_one_to_str(quest)])
                    col_one_keys.append(quest.key)
                if self.include_tasks:
                    for task in quest.tasks:
                        data.append([self.col_one_to_str(task)])
                        col_one_keys.append(task.key)
        # linha 1
        for user in self.row_one:
            data[0].append(user)
        # print("\n".join(map(str, data)))

        # preencher o resto com campos vazios
        for i in range(1, len(data)):
            if len(data[i]) < len(data[0]):
                data[i].extend([''] * (len(data[0]) - len(data[i])))

        # preencher os dados
        for r in range(1, len(data)):
            for c in range(1, len(data[0])):
                user = data[0][c]
                quest_or_task_key = col_one_keys[r]
                if quest_or_task_key in self.inside[user]:
                    data[r][c] = self.inside[user][quest_or_task_key]
                else:
                    data[r][c] = '---'
        return data


class Join:
    @staticmethod
    def decode_students_collected_file(file: str) -> dict[str, Collected]:
        if not os.path.isfile(file):
            print(f"Collected data file not found: {file}")
            exit(1)
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            user_info_map: dict[str, Collected] = {}
            for folder, text in data.items():
                collected_data = Collected().load_from_dict(json.loads(text))
                user_info_map[folder] = collected_data
        return user_info_map

    @staticmethod
    def join_student_daily_graph(user_info_map: dict[str, Collected]) -> str:
        lines: list[str] = []
        for folder, info in user_info_map.items():
            lines.append("─" * 120)
            lines.append(folder)
            lines.append(info.graph)
            lines.append("\n")
        return "\n".join(lines)

    @staticmethod
    def save_daily_graphs(class_task: ClassTask, user_info_map: dict[str, Collected]) -> None:
        graph_color, graph_mono = class_task.get_default_graph_joined()
        class_graph = Join.join_student_daily_graph(user_info_map)
        with open(graph_color, "w", encoding="utf-8") as f:
            f.write(class_graph)
        with open(graph_mono, "w", encoding="utf-8") as f:
            f.write(clear_ansi_codes(class_graph))

    @staticmethod
    def main(target: str) -> None:
        class_task = ClassTask(target).load_from_file()
        collected_path = class_task.get_default_collected()
        user_info_map = Join.decode_students_collected_file(collected_path)
        Join.save_daily_graphs(class_task, user_info_map)
        ref_folder = class_task.get_reference_rep()
        if ref_folder is not None:
            params = CmdRep.CollectParams()
            params.folder = ref_folder
            params.game = True
            params.json_output = True # dont echo
            reference: Collected = CmdRep.collect(params)
        else:
            reference: Collected = list(user_info_map.values())[0] # TODO

        # simple csv
        grid: Grid = Grid(user_info_map).set_reference(reference)
        path = class_task.get_default_simple_csv()
        CSV.save_csv(path, CSV.format_sheet(grid.build_csv()))

        # quest csv
        grid.set_include_tasks(False)
        path = class_task.get_default_quest_csv()
        CSV.save_csv(path, CSV.format_sheet(grid.build_csv()))

        # full csv
        grid.set_include_tasks(True).set_task_resume_to_str_function(task_resume_to_full_str)
        path = class_task.get_default_full_csv()
        CSV.save_csv(path, CSV.format_sheet(grid.build_csv()))
