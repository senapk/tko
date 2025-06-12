from tko.game.task import Task

import os
import re

class TaskParser:

    def __init__(self, index_path: str, database_folder: str):
        self.index_path = os.path.abspath(index_path) # path of Repository Root Readme file
        self.database_folder = os.path.abspath(database_folder)
        self.task = Task()

    def __load_xp(self, tags_raw: str):
        tags = [tag.strip() for tag in tags_raw.split(" ")]
        for t in tags:
            if t.startswith("+"):
                self.task.xp = int(t[1:])
                self.task.opt = True
            elif t.startswith("*"):
                self.task.xp = int(t[1:])
                self.task.opt = False
            

    def parse_line(self, line: str, line_num: int = 0) -> Task | None:
        pattern = r'\s*?- \[ \](.*?)\[([^\]]+)\]\(([^)]+)\)(?:\s*<!--(.*?)-->)?'

        match = re.match(pattern, line)
        if match is None:
            return None
        task = self.task
        task.line_number = line_num
        task.line = line
        task.title = match.group(1).strip()
        if task.title != "":
            task.title += " "
        task.title += match.group(2).strip()
        task.title = task.title.replace("`", "")
        self.__load_xp(task.title)

        if match.group(4) is not None:
            self.__load_xp(match.group(4))

        for item in task.title.split(" "):
            if item.startswith("@"):
                task.key = item[1:]
            elif item.startswith("#"):
                task.key = item[1:]
                task.link_type = Task.Types.VISITABLE_URL
            elif item == ":leet":
                task.set_leet(True)

        #remove last non alfa char from key
        allowed = "0123456789_abcdefghijklmnopqrstuvwxyz-ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        key = ""
        for c in task.key:
            if c in allowed:
                key += c
            else:
                break
        task.key = key

        link = match.group(3).strip()
        self.select_link_type(link)

        if task.key == "":
            task.key = link
        return task

    def select_link_type(self, link: str):
        task = self.task
        task.link = link

        if task.link_type == Task.Types.VISITABLE_URL:
            # open both url and files
            return

        if self.task.key == "":
            raise Warning(f"Chave não definida para tarefa: {link}")

        if link.startswith("http:") or link.startswith("https:"):
            task.set_folder(os.path.relpath(os.path.join(self.database_folder, task.key)))
            task.link_type = Task.Types.REMOTE_FILE
            return

        if not os.path.isabs(link):
            basedir = os.path.dirname(self.index_path)
            link = os.path.join(basedir, link)
            task.link = os.path.relpath(link)
        # verify if file exists
        # update link using index_path to update de relative path
        if not os.path.isfile(link):
            raise Warning(f"Arquivo não encontrado: {link}")

        # verify if file is inside database_folder/folder
        abs_task_folder = os.path.abspath(os.path.join(self.database_folder, task.key))
        task.set_folder(os.path.relpath(abs_task_folder))
        if link.startswith(abs_task_folder):
            task.link_type = Task.Types.STATIC_FILE
            return

        task.link_type = Task.Types.IMPORT_FILE
        return