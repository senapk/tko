#!/usr/bin/env python3

import argparse
import subprocess
import re
from typing import Optional, Dict, List
import os
from .format import colour, GSym, red, green, yellow
from .settings import RepoSettings as RepoSettings
  

class Task:

  def __init__(self):
    self.line_number = 0
    self.line = ""
    self.key = ""
    self.grade = ""
    self.skills = []
    self.title = ""
    self.link = ""

  def get_grade(self):
    if self.grade == "":
      return red(GSym.uncheck)
    if self.grade == "x":
      return green(GSym.check)
    number = int(self.grade)
    if number < 7:
      return red(GSym.numbers[number])
    return yellow(GSym.numbers[number])

  def get_percent(self):
    if self.grade == "":
      return 0
    if self.grade == "x":
      return 100
    return int(self.grade) * 10

  def is_done(self):
    return self.grade == "x" or self.grade == "7" or self.grade == "8" or self.grade == "9"
  
  def set_grade(self, grade):
    valid = ["", "x", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    if grade in valid:
      self.grade = grade
      return
    if grade == "0":
      self.grade = ""
      return
    if grade == "10":
      self.grade = "x"
      return
    print(f"Grade inválida: {grade}")

  def __str__(self):
    return f"{self.line_number} : {self.key} : {self.grade} : {self.title} : {self.skills} : {self.link}"

  @staticmethod
  def parse_titulo_link_html(line):
    # Regex para extrair o título e o link
    titulo_link_regex = r'\s*-.*\[(.*?)\](\(.+?\))'
    titulo_link_match = re.search(titulo_link_regex, line)

    # Regex para extrair as tags
    html_regex = r'<!--\s*(.*?)\s*-->'
    html_match = re.search(html_regex, line)

    # Inicializa as variáveis de título, link e html
    titulo = None
    link = None
    html = []

    # Extrai título e link
    if titulo_link_match:
      titulo = titulo_link_match.group(1).strip()
      link = titulo_link_match.group(2).strip('()')

    # Extrai html
    if html_match:
      html_raw = html_match.group(1).strip()
      html = [tag.strip() for tag in html_raw.split()]

    return titulo, link, html

  # coding tasks
  def set_key_from_title(self, titulo, html):
    title_key = titulo.split("@")[1]
    title_key = title_key.split(" ")[0]
    title_key = title_key.split(":")[0]
    title_key = title_key.split("/")[0]
    self.key = title_key
    self.skills = html
    self.coding = True

  # non coding tasks
  def set_key_from_html(self, html):
    html_key = [t for t in html if t.startswith("@")][0]
    html_key = html_key.split("@")[1]
    self.key = html_key
    self.coding = False
    self.skills = [t[2:] for t in html if t.startswith("s:")]

  def process_link(self, basefile):
    if self.link.startswith("http"):
      return
    if self.link.startswith("./"):
      self.link = self.link[2:]

    # todo trocar / por \\ se windows

    self.link = basefile + self.link

  def parse_task(self, line, line_num):
    if line == "":
      return False
    line = line.lstrip()

    titulo, link, html = Task.parse_titulo_link_html(line)

    if titulo is None:
      return False

    self.line = line
    self.line_number = line_num
    self.title = titulo
    self.link = link

    try:
      self.set_key_from_title(titulo, html)
      return True
    except:
      pass
    try:
      self.set_key_from_html(html)
      return True
    except:
      pass

    return False


class Quest:

  def __init__(self):
    self.line_number = 0
    self.line = ""
    self.key = ""
    self.title = ""
    self.mdlink = ""
    self.tasks = []
    self.skills = []
    self.group = ""
    self.requires = []
    self.requires_ptr = []
    self.type = "main"

  def __str__(self):
    return f"linha={self.line_number} : {self.key} : {self.title} : {self.skills} : {self.requires} : {self.mdlink} : {[t.key for t in self.tasks]}"

  def is_complete(self):
    return all([t.is_done() for t in self.tasks])

  def get_percent(self):
    total = len(self.tasks)
    if total == 0:
      return 0
    done = sum([t.get_percent() for t in self.tasks])
    return done // total

  def in_progress(self):
    if self.is_complete():
      return False
    for t in self.tasks:
      if t.grade != "":
        return True
    return False
  
  def not_started(self):
    if self.is_complete():
      return False
    if self.in_progress():
      return False
    return True

  def is_reachable(self, cache):
    if self.key in cache:
      return cache[self.key]

    if len(self.requires_ptr) == 0:
      cache[self.key] = True
      return True
    cache[self.key] = all(
        [r.is_complete() and r.is_reachable(cache) for r in self.requires_ptr])
    return cache[self.key]

  def parse_quest(self, line, line_num):
    pattern = r'^#+\s*(.*?)<!--\s*(.*?)\s*-->\s*$'
    match = re.match(pattern, line)
    titulo = None
    tags = []

    if match:
      titulo = match.group(1)
      tags_raw = match.group(2).strip()
      tags = [tag.strip() for tag in tags_raw.split()]
    else:
      pattern = r'^#+\s*(.*?)\s*$'
      match = re.match(pattern, line)
      if match:
        titulo = match.group(1)
        tags.append("@" + get_md_link(titulo))
      else:
        return False

    try:
      key = [t[1:] for t in tags if t.startswith("@")][0]
      self.line = line
      self.line_number = line_num
      self.title = titulo
      self.skills = [t[2:] for t in tags if t.startswith("s:")]
      self.requires = [t[2:] for t in tags if t.startswith("r:")]
      self.mdlink = "#" + get_md_link(titulo)
      groups = [t[2:] for t in tags if t.startswith("g:")]
      if len(groups) > 0:
        self.group = groups[0]
      else:
        self.group = ""
      type = [t for t in tags if t.startswith("t:")]
      if len(type) > 0:
        self.type = type[0][2:]
      self.key = key
      return True
    except Exception as e:
      print(e)
      return False

def rm_comments(title: str) -> str:
  if "<!--" in title and "-->" in title:
    title = title.split("<!--")[0] + title.split("-->")[1]
  return title

def get_md_link(title: str) -> str:
  if title is None:
    return ""
  title = title.lower()
  out = ''
  for c in title:
    if c == ' ' or c == '-':
      out += '-'
    elif c == '_':
      out += '_'
    elif c.isalnum():
      out += c
  return out

class Game:

  def __init__(self, file: Optional[str] = None):
    self.quests: Dict[str, Quest] = {} # quests indexed by quest key
    self.tasks: Dict[str, Task] = {}   # tasks  indexed by task key
    if file is not None:
      self.parse_file(file)

  def get_task(self, key: str) -> Task:
    if key in self.tasks:
      return self.tasks[key]
    raise Exception(f"fail: task {key} not found in course definition")

  def load_quest(self, line, line_num):
    quest = Quest()
    if not quest.parse_quest(line, line_num + 1):
      return (False, None)
    if quest.key in self.quests:
      print(f"Quest {quest.key} já existe")
      print(quest)
      print(self.quests[quest.key])
      exit(1)
    self.quests[quest.key] = quest
    return (True, quest)

  def load_task(self, line, line_num, last_quest):
    task = Task()
    if not task.parse_task(line, line_num + 1):
      return False
    if last_quest is None:
      print(f"Task {task.key} não está dentro de uma quest")
      print(task)
      exit(1)
    last_quest.tasks.append(task)
    if task.key in self.tasks:
      print(f"Task {task.key} já existe")
      print(task)
      print(self.tasks[task.key])
      exit(1)
    self.tasks[task.key] = task
    return True

  # Verificar se todas as quests requeridas existem e adiciona o ponteiro
  # Verifica se todas as quests tem tarefas
  def validate_requirements(self):
    #remove all quests without tasks
    valid_quests = {}
    for k, q in self.quests.items():
      if len(q.tasks) > 0:
        valid_quests[k] = q

    self.quests = valid_quests

    # for q in self.quests.values():
    #   if len(q.tasks) == 0:
    #     print(f"Quest {q.key} não tem tarefas")
    #     exit(1)

    for q in self.quests.values():
      for r in q.requires:
        if r in self.quests:
          q.requires_ptr.append(self.quests[r])
        else:
          print(f"Quest\n{str(q)}\nrequer {r} que não existe")
          exit(1)

    #check if there is a cycle

  def check_cycle(self):

    def dfs(q, visited):
      if len(visited) > 0:
        if visited[0] == q.key:
          print(f"Cycle detected: {visited}")
          exit(1)
      if q.key in visited:
        return
      visited.append(q.key)
      for r in q.requires_ptr:
        dfs(r, visited)

    for q in self.quests.values():
      visited = []
      dfs(q, visited)

  def parse_file(self, file):
    lines = open(file).read().split("\n")
    last_quest = None
    for index, line in enumerate(lines):
      found, quest = self.load_quest(line, index)
      if found:
        last_quest = quest
      else:
        self.load_task(line, index, last_quest)
    self.validate_requirements()
    for t in self.tasks.values():
      t.process_link(os.path.dirname(file) + "/")

  def get_reachable_quests(self):
    # cache needs to be reseted before each call
    cache = {}
    return [q for q in self.quests.values() if q.is_reachable(cache)]

  def show_quests(self):
    print( f"Quests de Entrada: {[q.key for q in self.quests.values() if len(q.requires) == 0]}" )
    print(f"Total de quests: {len(self.quests)}")
    print("\n".join([str(q) for q in self.quests.values()]))

  def generate_graph(self, output):
    saida = []
    saida.append(f"@startuml {output}")
    saida.append("digraph diag {")
    saida.append('  node [style="rounded,filled", shape=box]')

    def info(q):
      return f"\"{q.title.strip()}:{len(q.tasks)}\""

    for q in self.quests.values():
      token = "->"
      if len(q.requires_ptr) > 0:
        for r in q.requires_ptr:
          saida.append(f"  {info(r)} {token} {info(q)}")
      else:
        v = "  \"Início\""
        saida.append(f"{v} {token} {info(q)}")

    for q in self.quests.values():
      if q.type == "main":
        saida.append(f"  {info(q)} [fillcolor=lime]")
      else:
        saida.append(f"  {info(q)} [fillcolor=pink]")

    groups = {}
    for q in self.quests.values():
      if q.group == "":
        continue
      if q.group not in groups:
        groups[q.group] = []
      groups[q.group].append(q)

    for c in groups.values():
      if c == "":
        continue
      saida.append(f"  subgraph cluster_{c[0].group} {{")
      saida.append(f"    label=\"{c[0].group}\"")
      saida.append(f"    style=filled")
      saida.append(f"    color=lightgray")
      for q in c:
        saida.append(f"    {info(q)}")

      saida.append("  }")

    saida.append("}")
    saida.append("@enduml")
    saida.append("")

    open(output + ".puml", "w").write("\n".join(saida))
    subprocess.run(["plantuml", output + ".puml", "-tsvg"])

