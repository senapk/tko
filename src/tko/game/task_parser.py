from __future__ import annotations
from tko.game.task import Task

import os
import re
from icecream import ic # type: ignore
from pathlib import Path

class TaskParser:

    def __init__(self, index_path: Path, source_alias: str):
        self.index_path = index_path
        self.task: Task | None = Task().set_remote_name(source_alias)
            
    @staticmethod
    def filter_task_key(key: str) -> str:
        allowed = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_+"
        new_key = ""
        for c in key:
            if c in allowed:
                new_key += c
            else:
                break
        return new_key

    # returns
    # tuple[bool, title, html_tags, link]
    def match_full_pattern(self, line: str) -> tuple[bool, str, str, str]:
        pattern = r'\s*?- \[ \](.*?)\[([^\]]+)\]\(([^)]+)\)?'
        match = re.match(pattern, line)
        if match is None:
            return False, "", "", ""
        tags = match.group(1).strip()
        tags = tags.replace("`", " ").replace("<!--", " ").replace("-->", " ")
        title = match.group(2).strip()
        link = match.group(3).strip()
        return True, tags, title, link

    def decode_task_types(self, info: str):
        if self.task is None:
            return
        self.task.task_loss = Task.TaskLoss.NULL
        self.task.task_test = Task.TaskTest.NULL
        for tag in info.split(":"):
            # if c is digit, set xp
            if tag.isdigit():
                self.task.xp = int(tag)
            elif tag == Task.TaskTest.TEST.value:
                self.task.task_test = Task.TaskTest.TEST
            elif tag == Task.TaskTest.SELF.value:
                self.task.task_test = Task.TaskTest.SELF
            elif tag == Task.TaskMain.MAIN.value:
                self.task.task_path = Task.TaskMain.MAIN
            elif tag == Task.TaskMain.SIDE.value:
                self.task.task_path = Task.TaskMain.SIDE
            elif tag == Task.TaskLoss.FREE.value:
                self.task.task_loss = Task.TaskLoss.FREE
            elif tag == Task.TaskLoss.PART.value:
                self.task.task_loss = Task.TaskLoss.PART
            elif tag == Task.TaskLoss.ZERO.value:
                self.task.task_loss = Task.TaskLoss.ZERO
            else:
                print(f"Parsing {self.index_path}:{self.task.line_number}, Tipo de tarefa desconhecido: {tag}")

    def __parse_key_task_types(self, tags: str) -> str:
        if self.task is None:
            return ""
        new_title: list[str] = []
        words = [w for w in tags.split(" ") if w != ""]
        self.task.task_loss = Task.TaskLoss.NULL
        for item in words:
            if item.startswith("@"):
                self.task.set_key(self.filter_task_key(item[1:]))
            elif item.startswith(":"):
                self.decode_task_types(item[1:])
            else:
                new_title.append(item)

        if self.task.get_key().startswith("+"):
            self.task.task_mode = Task.TaskEdit.VIEW
        else:
            self.task.task_mode = Task.TaskEdit.EDIT
        
        if self.task.task_mode == Task.TaskEdit.VIEW:
            if self.task.task_loss == Task.TaskLoss.NULL:
                self.task.task_loss = Task.TaskLoss.FREE
            if self.task.task_test == Task.TaskTest.NULL:
                self.task.task_test = Task.TaskTest.SELF
        else: # EDIT
            if self.task.task_loss == Task.TaskLoss.NULL:
                self.task.task_loss = Task.TaskLoss.PART
            if self.task.task_test == Task.TaskTest.NULL:
                self.task.task_test = Task.TaskTest.TEST

        return " ".join(new_title)

    def redirect_from_readme(self, link: str) -> str:
        if not os.path.isabs(link):
            basedir = os.path.dirname(self.index_path)
            target = os.path.join(basedir, link)
            return target
        return link

    def parse_line(self, line: str, line_num: int = 0) -> TaskParser:
        found, tags, title, link = self.match_full_pattern(line)
        if not found:
            self.task = None
        if self.task is None:
            return self
        
        task = self.task
        task.line_number = line_num
        task.line = line
        title = self.__parse_key_task_types(tags + " " + title)
        task.set_title(title)

        if task.get_key() == "":
            self.task = None
            return self

        if link.startswith("http://") or link.startswith("https://"):
            self.task.set_remote_view_type()
            self.task.target = link
            return self
        
        task.set_origin_folder(Path(os.path.dirname(self.redirect_from_readme(link))))
        if task.task_mode == Task.TaskEdit.VIEW:
            self.task.target = self.redirect_from_readme(link)
        else:
            self.task.target = link

        return self

    def get_task(self) -> Task | None:
        return self.task


    def check_path_try(self):
        if self.task is None:
            return self
        if self.task.is_import_type():
            relative_path = self.index_path.parent / self.task.target
            if not relative_path.exists():
                raise Warning(f"Parsing {self.index_path}, Arquivo de tarefa não encontrado: {self.task.target}")
        return self