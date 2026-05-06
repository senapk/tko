from __future__ import annotations
from tko.game.task import Task
from tko.game.task_config import TaskEdit, TaskLoss, TaskMain, TaskTest

import os
import re
from icecream import ic # type: ignore
from pathlib import Path

class TaskParser:

    def __init__(self, index_path: Path, source_alias: str):
        self.index_path = index_path
        self.task: Task | None = Task()
        self.task.identity.set_remote_name(source_alias)
            
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
        self.task.config.loss = TaskLoss.NULL
        self.task.config.test = TaskTest.NULL
        for tag in info.split(":"):
            # if c is digit, set xp
            if tag.isdigit():
                self.task.xp = int(tag)
            elif tag == TaskTest.TEST.value:
                self.task.config.test = TaskTest.TEST
            elif tag == TaskTest.SELF.value:
                self.task.config.test = TaskTest.SELF
            elif tag == TaskMain.MAIN.value:
                self.task.config.path = TaskMain.MAIN
            elif tag == TaskMain.SIDE.value:
                self.task.config.path = TaskMain.SIDE
            elif tag == TaskMain.PERK.value:
                self.task.config.path = TaskMain.PERK
            elif tag == TaskLoss.FREE.value:
                self.task.config.loss = TaskLoss.FREE
            elif tag == TaskLoss.PART.value:
                self.task.config.loss = TaskLoss.PART
            elif tag == TaskLoss.ZERO.value:
                self.task.config.loss = TaskLoss.ZERO
            else:
                    print(f"Parsing {self.index_path}:{self.task.location.line_number}, Tipo de tarefa desconhecido: {tag}")

    def __parse_key_task_types(self, tags: str) -> str:
        if self.task is None:
            return ""
        new_title: list[str] = []
        words = [w for w in tags.split(" ") if w != ""]
        self.task.config.loss = TaskLoss.NULL
        for item in words:
            if item.startswith("@"):
                self.task.identity.set_key(self.filter_task_key(item[1:]))
            elif item.startswith(":"):
                self.decode_task_types(item[1:])
            else:
                new_title.append(item)

        if self.task.identity.get_key().startswith("+"):
            self.task.config.mode = TaskEdit.VIEW
        else:
            self.task.config.mode = TaskEdit.EDIT
        
        if self.task.config.mode == TaskEdit.VIEW:
            if self.task.config.loss == TaskLoss.NULL:
                self.task.config.loss = TaskLoss.FREE
            if self.task.config.test == TaskTest.NULL:
                self.task.config.test = TaskTest.SELF
        else: # EDIT
            if self.task.config.loss == TaskLoss.NULL:
                self.task.config.loss = TaskLoss.PART
            if self.task.config.test == TaskTest.NULL:
                self.task.config.test = TaskTest.TEST

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
        task.location.line_number = line_num
        task.location.line = line
        title = self.__parse_key_task_types(tags + " " + title)
        task.identity.set_title(title)

        if task.identity.get_key() == "":
            self.task = None
            return self

        if link.startswith("http://") or link.startswith("https://"):
            self.task.location.set_remote_view_type()
            self.task.location.target = link
            return self
        
        task.location.set_origin_folder(Path(os.path.dirname(self.redirect_from_readme(link))))
        if task.config.mode == TaskEdit.VIEW:
            self.task.location.target = self.redirect_from_readme(link)
        else:
            self.task.location.target = link

        return self

    def get_task(self) -> Task | None:
        return self.task

    def check_path_try(self):
        if self.task is None:
            return self
        if self.task.is_import_type():
            relative_path = self.index_path.parent / self.task.location.target
            if not relative_path.exists():
                raise Warning(f"Parsing {self.index_path}, Arquivo de tarefa não encontrado: {self.task.location.target}")
        return self