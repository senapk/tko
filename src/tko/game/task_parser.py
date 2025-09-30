from tko.game.task import Task

import os
import re
from icecream import ic # type: ignore


"""
Task can be:
- Link do remote url (http, https)
- Link para arquivo local (Readme.md com link para arquivos locais)
  - O source link está fora da pasta do rep
  - apontando para o ghost ou arcade em outra pasta
  - apontando para o clone automático do arcade em outra pasta
- Se abrir o tko init dentro do arcade para fazer as questões no próprio rep
  - o Readme.md está dentro do rep
  - o readme aponta para paths de tarefas dentro do database
  - o alias do rep tem que ser o mesmo do database, ou seja base
  - tko init --alias base --link Readme.md

- Conseguir carregar valor e tags também a partir do título
  - por exemplo, se é leet
  - se é opcional ou obrigatório e o valor usando a tag da quest (*10, +5)
"""

class TaskParser:

    def __init__(self, index_path: str, database: str, rep_folder_path: str):
        self.index_path = os.path.abspath(index_path) # path of Repository Root Readme file
        self.database_folder = os.path.abspath(os.path.join(rep_folder_path, database)) # path of database folder inside rep
        self.task = Task().set_database(database).set_rep_folder(rep_folder_path)

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
        title = match.group(1).strip()
        if title != "":
            title += " "
        title += match.group(2).strip()
        title = title.replace("`", "")
        task.set_title(title)
        self.__load_xp(task.get_title())

        if match.group(4) is not None:
            self.__load_xp(match.group(4))

        for item in task.get_title().split(" "):
            if item.startswith("@"):
                task.set_key(item[1:])
            elif item.startswith("#"):
                task.set_key(item[1:])
                task.link_type = Task.Types.VISITABLE_URL
            elif item == ":leet":
                task.set_leet(True)

        #remove last non alfa char from key
        allowed = "0123456789_abcdefghijklmnopqrstuvwxyz-ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        key = ""
        for c in task.get_only_key():
            if c in allowed:
                key += c
            else:
                break
        task.set_key(key)

        link = match.group(3).strip()
        self.select_link_type(link)

        if task.get_only_key() == "":
            task.set_key(link)
        return task

    def select_link_type(self, link: str):
        task = self.task
        task.link = link

        if task.link_type == Task.Types.VISITABLE_URL:
            # open both url and files
            return

        if self.task.get_only_key() == "":
            raise Warning(f"Parsing {self.index_path}, Chave de tarefa não definida: {link}")

        if link.startswith("http:") or link.startswith("https:"):
            task.link_type = Task.Types.REMOTE_FILE
            return
        if not os.path.isabs(link):
            basedir = os.path.dirname(self.index_path)
            link = os.path.join(basedir, link)
            task.link = os.path.relpath(link)
        # verify if file exists
        # update link using index_path to update de relative path
        if not os.path.isfile(link):
            raise Warning(f"Parsing {self.index_path}, Arquivo de tarefa não encontrado: {link}")


        task.link_type = Task.Types.IMPORT_FILE
        return