#!/usr/bin/env python3
from __future__ import annotations
import os
import argparse
import re
import json
from .paths import Paths
from .collected_data import CollectedData
from .class_task import ClassTask
from tko.logger.task_resume import TaskResume
from .collect import Collect
from .pull import pull_class_task
import csv

def clear_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from a string."""
    ansi_escape = re.compile(r'\x1B\[[0-?9;]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


def join_student_daily_graph(user_info_map: dict[str, CollectedData]) -> str:
    lines: list[str] = []
    for folder, info in user_info_map.items():
        lines.append("─" * 120)
        lines.append(folder)
        lines.append(info.graph)
        lines.append("\n")
    return "\n".join(lines)


def decode_student_info_file(file: str) -> dict[str, CollectedData]:
    if not os.path.isfile(file):
        print(f"Collected data file not found: {file}")
        exit(1)
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        user_info_map: dict[str, CollectedData] = {}
        for folder, text in data.items():
            collected_data = CollectedData().load_from_dict(json.loads(text))
            user_info_map[folder] = collected_data
    return user_info_map

class Grid:
    def __init__(self, row_one: list[str], col_one: list[str], data: list[list[TaskResume]]):
        self.row_one: list[str] = row_one
        self.col_one: list[str] = col_one
        self.data: list[list[TaskResume]] = data

class Join:
    @staticmethod
    def save_daily_graphs(class_task: ClassTask, user_info_map: dict[str, CollectedData]) -> None:
        graph_color, graph_mono = Paths.get_default_graph_joined(class_task)
        class_graph = join_student_daily_graph(user_info_map)
        with open(graph_color, "w", encoding="utf-8") as f:
            f.write(class_graph)
        with open(graph_mono, "w", encoding="utf-8") as f:
            f.write(clear_ansi_codes(class_graph))

    @staticmethod
    def make_grid(reference: CollectedData, user_info_map: dict[str, CollectedData]) -> Grid:
        user_label_task: dict[str, dict[str, TaskResume]] = {}
        for folder, info in user_info_map.items():
            user_label_task[folder] = info.resume

        col_one: list[str] = []
        row_one = sorted(user_label_task.keys())
        for quest in reference.game:
            col_one.append(f'{quest.key}:{quest.value}:{'*' if quest.opt else '+'}')
            for task in quest.tasks:
                col_one.append(f'{task.key}:{task.xp}:{'*' if task.opt else '+'}')

        inside: list[list[TaskResume]] = [[] for _ in  range(len(col_one))]
        for user in row_one:
            for i, kvopt in enumerate(col_one):
                key = kvopt.split(":")[0]
                if key in user_label_task[user]:
                    inside[i].append(user_label_task[user][key])
                else:
                    inside[i].append(TaskResume())
        
        grid = Grid(col_one=col_one, row_one=row_one, data=inside)
        return grid
    
    @staticmethod
    def make_simple_csv(class_task: ClassTask, grid: Grid) -> list[list[str]]:
        data: list[list[str]] = []
        for i, col in enumerate(grid.col_one):
            data.append([])
            data[i].append(col)
            for task in grid.data[i]:
                data[i].append(f'{task.info.rate}')
        header = ['SIMPLE'] + [x for x in grid.row_one]
        data = [header] + data
        csv_path = Paths.get_default_simple_csv(class_task)
        save_csv(csv_path, sheet=data)
        return data
    

    @staticmethod
    def main(args: argparse.Namespace) -> None:
        class_task = ClassTask().load_from_file(args.target)
        collected_path = Paths.get_default_collected(class_task)
        user_info_map = decode_student_info_file(collected_path)
        Join.save_daily_graphs(class_task, user_info_map)
        reference: CollectedData = list(user_info_map.values())[0] # TODO
        grid = Join.make_grid(reference, user_info_map)
        Join.make_simple_csv(class_task, grid)


def load_csv(arquivo_csv: str) -> list[list[str]]:
    try:
        with open(arquivo_csv, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            sheet = list(reader)
            return sheet
    except FileNotFoundError:
        exit(f"Arquivo '{arquivo_csv}' não encontrado.")

def save_csv(arquivo_csv: str, sheet: list[list[str]]):
    try:
        with open(arquivo_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sheet)
    except FileNotFoundError:
        exit(f"Arquivo '{arquivo_csv}' não encontrado.")

def pull(args: argparse.Namespace) -> None:
    pull_class_task(args.target, args.threads)

def tejo_main():
    # Caminho do arquivo CSV
    parser = argparse.ArgumentParser(description="Ferramenta para lidar com tarefas do classroom usando o tko.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    pull_cmd = subcommands.add_parser("pull", help="Pull data from the specified target.")
    pull_cmd.add_argument("target", type=str, help="Json class task file")
    pull_cmd.add_argument("-t", "--threads", type=int, default=5, help="Number of threads to use for pulling data.")
    pull_cmd.set_defaults(func=pull)

    collect_cmd = subcommands.add_parser("collect", help="Collect data from the specified target.")
    collect_cmd.add_argument("target", type=str, help="Json class task file")
    collect_cmd.set_defaults(func=Collect.main)

    join_cmd = subcommands.add_parser("join", help="Join collected data from the specified target.")
    join_cmd.add_argument("target", type=str, help="Json class task file")
    join_cmd.set_defaults(func=Join.main)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    tejo_main()
