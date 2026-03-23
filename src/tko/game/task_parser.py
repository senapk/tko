from __future__ import annotations
from tko.game.task import Task

import os
import re
from icecream import ic # type: ignore
from pathlib import Path

class TaskParser:

    def __init__(self, index_path: Path, source_alias: str):
        self.index_path = index_path
        self.task: Task | None = Task().set_alias(source_alias)
            
    @staticmethod
    def filter_task_key(key: str) -> str:
        allowed = "0123456789_abcdefghijklmnopqrstuvwxyz-ABCDEFGHIJKLMNOPQRSTUVWXYZ"
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
        pattern = r'\s*?- \[ \](.*?)\[([^\]]+)\]\(([^)]+)\)(?:\s*<!--(.*?)-->)?'
        match = re.match(pattern, line)
        if match is None:
            return False, "", "", ""
        title = match.group(1).strip()
        if title != "":
            title += " "
        title += match.group(2).strip()
        title = title.replace("`", "")
        html_tags = match.group(4).strip() if match.group(4) is not None else ""
        link = match.group(3).strip()
        return True, title, html_tags, link

    def decode_task_types(self, info: str):
        if self.task is None:
            return
        for c in info:
            # if c is digit, set xp
            if c.isdigit():
                self.task.xp = int(c)
            elif c == "t":
                self.task.task_rate = Task.TaskRate.TEST
            elif c == "s":
                self.task.task_rate = Task.TaskRate.SELF
            elif c == "i":
                self.task.task_rate = Task.TaskRate.INFO
            elif c == "=":
                self.task.task_path = Task.TaskPath.MAIN
            elif c == "+":
                self.task.task_path = Task.TaskPath.SIDE
            elif c == "?":
                self.task.task_rule = Task.TaskRule.MOCK
            elif c == "!":
                self.task.task_rule = Task.TaskRule.EXAM

    def __parse_key_task_types(self, tags_raw: str) -> str:
        if self.task is None:
            return ""
        new_title: list[str] = []
        for item in tags_raw.split(" "):
            if item.startswith("@"):
                self.task.set_key(self.filter_task_key(item[1:]))
                new_title.append(item)
            elif item.startswith(":"):
                self.decode_task_types(item[1:])
            else:
                new_title.append(item)
        return " ".join(new_title)



    def redirect_from_readme(self, link: str) -> str:
        if not os.path.isabs(link):
            basedir = os.path.dirname(self.index_path)
            target = os.path.join(basedir, link)
            return target
        return link

    def parse_line(self, line: str, line_num: int = 0) -> TaskParser:
        found, title, html_tags, link = self.match_full_pattern(line)
        if not found:
            self.task = None
        if self.task is None:
            return self
        
        task = self.task
        task.line_number = line_num
        task.line = line
        title = self.__parse_key_task_types(title + " " + html_tags)
        task.set_title(title)

        if link.startswith("http://") or link.startswith("https://"):
            self.task.set_link_type()
            self.task.set_key(link)
            self.task.target = link
            return self
        
        if self.task.get_key_only() == "": # não tem chave, e não é url
            self.task.set_link_type()
            self.task.set_key(link)
            self.task.target = self.redirect_from_readme(link)
            return self
        
        self.task.target = link
        task.set_origin_folder(Path(os.path.dirname(self.redirect_from_readme(link))))

        return self

    def get_task(self) -> Task | None:
        return self.task


    def check_path_try(self):
        if self.task is None:
            return self
        if self.task.is_import_type():
            if not os.path.isfile(self.task.target):
                raise Warning(f"Parsing {self.index_path}, Arquivo de tarefa não encontrado: {self.task.target}")
        return self