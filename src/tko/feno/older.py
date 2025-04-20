from typing import Tuple
import os
import glob
from os.path import getmtime
import argparse


class Older:
    # return the last update for the most recent file in the directory
    @staticmethod
    def last_update(path: str) -> Tuple[str, float]:
        value = None
        if os.path.isfile(path):
            value = (path, getmtime(path))
        else:
            file_list = list(glob.iglob(path + '/**', recursive=True))
            file_list = [f for f in file_list if os.path.isfile(f)]
            if len(file_list) == 0:
                value = (path, getmtime(path))
            else:
                juntos = [(f, getmtime(f)) for f in file_list]
                value = max(juntos, key=lambda x: x[1])
        return value

    # busca recursivamente o arquivo mais recente dentro os arquivos passados
    @staticmethod
    def find_older(targets: list[str]) -> str:
        best_file, best_time = Older.last_update(targets[0])
        for target in targets[1:]:
            file, time = Older.last_update(target)
            if time > best_time:
                best_file, best_time = file, time
        return best_file

def older_main(args: argparse.Namespace):
    print(Older.find_older(args.targets))
