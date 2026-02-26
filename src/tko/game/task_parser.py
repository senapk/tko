from __future__ import annotations
from tko.game.task import Task

import os
import re
from icecream import ic # type: ignore


class TaskParser:

    def __init__(self, index_path: str, source_alias: str):
        self.index_path = index_path
        self.task: Task | None = Task().set_source_alias(source_alias)

    def __load_xp(self, tags_raw: str):
        if self.task is None:
            return
        tags = [tag.strip() for tag in tags_raw.split(" ")]
        for t in tags:
            if t.startswith("+"):
                self.task.xp = int(t[1:])
                self.task.opt = True
            elif t.startswith("*"):
                self.task.xp = int(t[1:])
                self.task.opt = False
            

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

    def __parse_key_leet_solo(self, tags_raw: str):
        if self.task is None:
            return
        for item in tags_raw.split(" "):
            if item.startswith("@"):
                self.task.set_key(self.filter_task_key(item[1:]))
            elif item == ":leet":
                self.task.set_leet()
            elif item == ":solo":
                self.task.set_solo()
                self.task.set_leet()

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
        task.set_title(title)
        self.__load_xp(task.get_title() + " " + html_tags)
        self.__parse_key_leet_solo(title + " " + html_tags)

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
        task.set_origin_folder(self.redirect_from_readme(link))

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