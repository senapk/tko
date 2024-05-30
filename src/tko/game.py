#!/usr/bin/env python3

import argparse
import subprocess
import re
from typing import Optional, Dict, List
import os
import shutil
from .format import colour
from .settings import RepoSettings as RepoSettings
from .remote import RemoteCfg
import tempfile

class GSym:
  check = "✓" #"✅" "☑" "🮱"
  uncheck = "✗" # "❎" "☐" "🯀"
  vcheck = "@" # "☑"
  vuncheck = "#" # "☐"
  numbers = ["𝟬","𝟭","𝟮","𝟯","𝟰","𝟱","𝟲","𝟳","𝟴","𝟵"]

def green(text):
  return colour("g", text)

def red(text):
  return colour("r", text)

def yellow(text):
  return colour("y", text)

def cyan(text):
  return colour("c", text)
  

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
  def set_key_from_html(self, titulo, html):
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
      self.set_key_from_html(titulo, html)
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

  def __init__(self):
    self.quests: Dict[str, Quest] = {} # quests indexed by quest key
    self.tasks: Dict[str, Task] = {}   # tasks  indexed by task key

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




class Play:

  def __init__(self, game: Game, rep: RepoSettings, fnsave):
    self.fnsave = fnsave
    self.rep = rep
    self.show_link = "link" in self.rep.view
    self.show_done = "done" in self.rep.view
    self.show_init = "init" in self.rep.view
    self.show_todo = "todo" in self.rep.view
    self.show_cmds = "cmds" in self.rep.view
    self.show_perc = "perc" in self.rep.view

    self.game: Game = game
    self.tasks: Dict[str, Task] = {}  # visible tasks  indexed by upper letter
    self.quests: Dict[str, Quest] = {} # visible quests indexed by number
    self.active: List[str] = [] # expanded quests

    for k, v in self.rep.quests.items():
      if "e" in v:
        self.active.append(k)

    self.term_limit = 130

    for key, grade in rep.tasks.items():
      if key in game.tasks:
        game.tasks[key].set_grade(grade)

  def read_link(self, link):
    if link.endswith(".md"):
      if link.startswith("https"):
        with tempfile.NamedTemporaryFile(delete=False) as f:
          file = f.name
          cfg = RemoteCfg()
          cfg.from_url(link)
          cfg.download_absolute(file)
          link = file
          # verify is subprocess succeeds
      result = subprocess.run(["glow", "-p", link])
      if result.returncode != 0:
        print(f"Erro ao abrir o arquivo {link}")
        print("Verifique se o arquivo está no formato markdown")
        input("Digite enter para continuar")
        

  def save_to_json(self):
    self.rep.quests = {}
    for q in self.active:
      self.rep.quests[q] = "e"
    self.rep.tasks = {}
    for t in self.game.tasks.values():
      if t.grade != "":
        self.rep.tasks[t.key] = t.grade
    self.rep.view = []
    if self.show_link:
      self.rep.view.append("link")
    if self.show_perc:
      self.rep.view.append("perc")
    if self.show_done:
      self.rep.view.append("done")
    if self.show_init:
      self.rep.view.append("init")
    if self.show_todo:
      self.rep.view.append("todo")
    if self.show_cmds:
      self.rep.view.append("cmds")
    self.fnsave()

  @staticmethod
  def calc_letter(index_letter):
    unit = index_letter % 26
    ten = index_letter // 26
    if ten == 0:
      return chr(ord("A") + unit)
    return chr(ord("A") + ten - 1) + chr(ord("A") + unit)

  @staticmethod
  def calc_index(letter):
    letter = letter.upper()
    if len(letter) == 1:
      return ord(letter) - ord("A")
    return (ord(letter[0]) - ord("A") + 1) * 26 + (ord(letter[1]) - ord("A"))

  def update_reachable(self):
    quests = self.game.get_reachable_quests()
    reach_keys = []
    reach_keys = [q.key for q in quests]
    menu_keys = [q.key for q in self.quests.values()]

    for key in menu_keys:
      if key not in reach_keys:
        self.quests = {}
        break

    if len(self.quests) == 0:
      index = 0
      for q in quests:
        self.quests[str(index)] = q
        index += 1
    else:
      index = len(self.quests.keys())
      for q in quests:
        if q.key not in menu_keys:
          self.quests[str(index)] = q
          index += 1

    self.active = set([k for k in self.active if k in reach_keys])

    # if len(self.quests.values()) == 1:
    #     for q in self.quests.values():
    #         self.active.add(q.key)


  def calculate_pad(self):
    titles = []
    keys = self.quests.keys()
    for key in keys:
      q = self.quests[key]
      titles.append(q.title)
      if q.key not in self.active:
        continue
      for t in q.tasks:
        titles.append(t.title)
    max_title = 10
    if (len(titles) > 0):
      max_title = max([len(t) for t in titles])
    return max_title

  def to_show_quest(self, quest: Quest):
    if quest.is_complete() and not self.show_done:
      return False
    if quest.not_started() and not self.show_todo:
      return False
    if quest.in_progress() and not self.show_init:
      return False
    return True


  def print_quest(self, entry, q, max_title, term_size):
    resume = ""
    opening = "➡️"
    if q.key in self.active:
      opening = "⬇️"
    done = len([t for t in q.tasks if t.is_done()])
    size = len(q.tasks)
    if done > 9:
      done = "*"
    if size > 9:
      size = "*"
    if self.show_perc:
      text = f" {str(q.get_percent()).rjust(3)}%"
    else:
      text = f"[{str(done)}/{str(size)}]"
    space = " " if len(entry) == 1 else ""
    if q.is_complete():
      resume = green(text)
    elif q.in_progress():
      resume = yellow(text)
    else:
      resume = red(text)
    entry = colour("b", entry) if q.type == "main" else colour("m", entry)
    qlink = ""
    if self.show_link:
      if term_size > self.term_limit:
        qlink = " " + colour("c", q.mdlink)
      else:
        qlink = "\n      " + colour("c", q.mdlink)
    if not self.to_show_quest(q):
      return
    title = q.title
    if self.show_link and term_size > self.term_limit:
      title = title.strip().ljust(max_title + 1)
    print(f"{opening} {space}{entry}{resume} {title}")

  def print_task(self, t, max_title, letter, term_size):
    vindex = str(letter).rjust(2, " ")
    vdone = t.get_grade()
    vlink = ""
    title = t.title
    if self.show_link:
      if t.key in t.title:
        vlink = red(t.link)
      else:
        vlink = yellow(t.link)
      if term_size > self.term_limit:
        title = t.title.strip().ljust(max_title + 1)
        vlink = " " + vlink
      else:
        vlink = "\n      " + vlink
    print(f"    {vindex} {vdone}  {title}{vlink}")

  def sort_keys(self, keys):
    single = [k for k in keys if len(str(k)) == 1]
    double = [k for k in keys if len(str(k)) == 2]
    return sorted(single) + sorted(double)

  def show_tasks(self):
    term_size = shutil.get_terminal_size().columns
    self.tasks = {}

    self.update_reachable()
    max_title = self.calculate_pad()
    index = 0
    for entry in self.sort_keys(self.quests.keys()):
      q = self.quests[entry]
      self.print_quest(entry, q, max_title, term_size)
      if q.key not in self.active:
        continue
      if not self.to_show_quest(q):
        continue
      for t in q.tasks:
        letter = self.calc_letter(index)
        self.print_task(t, max_title, letter, term_size)
        index += 1
        self.tasks[letter] = t

  @staticmethod
  def get_num_num(s):
    pattern = r'^(\d+)-(\d+)$'
    match = re.match(pattern, s)
    if match:
      return int(match.group(1)), int(match.group(2))
    else:
      return (None, None)

  @staticmethod
  def get_letter_letter(s):
    pattern =r'([a-zA-Z]+)-([a-zA-Z]+)'
    match = re.match(pattern, s)
    if match:
      print(match.group(1), match.group(2))
      return match.group(1), match.group(2)
    return (None, None)

  def expand_range(self, line) -> List[str]:
    line = line.replace(" - ", "-")
    actions = line.split()

    expand = []
    for t in actions:
      (start_number, end_number) = self.get_num_num(t)
      (start_letter, end_letter) = self.get_letter_letter(t)
      if start_number is not None and end_number is not None:
        expand += list(range(start_number, end_number + 1))
      elif start_letter is not None and end_letter is not None:
        start_index = self.calc_index(start_letter)
        end_index = self.calc_index(end_letter)
        print(start_index, end_index)
        expand += [self.calc_letter(i) for i in range(start_index, end_index + 1)]
      else:
        expand.append(t)
    return expand

  def clear(self):
    subprocess.run("clear")
    pass

  def is_number(self, s):
    try:
      int(s)
      return True
    except ValueError:
      return False
    
  def take_actions(self, actions):
    if len(actions) == 0:
      return
    cmd = actions[0]

    if cmd == "{":
      self.active = set()
    elif cmd == "}":
      self.update_reachable()
      self.active = set([q.key for q in self.quests.values()])
    elif cmd == "h" or cmd == "help":
      self.clear()
      self.show_help()
    elif cmd == "c" or cmd == "cmds":
      self.show_cmds = not self.show_cmds
    elif cmd == "a" or cmd == "all":
      self.show_done = True
      self.show_init = True
      self.show_todo = True
    elif cmd == "i" or cmd == "init":
      self.show_init = True
      self.show_done = False
      self.show_todo = False
    elif cmd == "d" or cmd == "done":
      self.show_done = True
      self.show_init = False
      self.show_todo = False
    elif cmd == "t" or cmd == "todo":
      self.show_todo = True
      self.show_done = False
      self.show_init = True
    elif cmd == "l" or cmd == "link":
      self.show_link = not self.show_link
    elif cmd == "p" or cmd == "perc":
      self.show_perc = not self.show_perc
    elif self.is_number(cmd):
      for t in actions:
        if self.is_number(t):
          if t in self.quests:
            key = self.quests[t].key
            if key not in self.active:
              self.active.add(key)
            else:
              self.active.remove(key)
          else:
            print(f"{t} não processado")
            input("Digite enter para continuar")
    elif cmd[0].isupper():
      for t in actions:
        letter = "".join([c for c in t if c.isupper() and not c.isdigit()])
        number = "".join([c for c in t if c.isdigit()])
        if letter in self.tasks:
          t = self.tasks[letter]
          if len(number) > 0:
            t.set_grade(number)
          else:
            if t.grade == "":
              t.set_grade("x")
            else:
              t.set_grade("")
        else:
          print(f"{t} não processado")
          input("Digite enter para continuar")
    elif cmd == "r" or cmd == "read":
      if len(actions) > 1:
        if actions[1] in self.tasks:
          print(self.tasks[actions[1]].link)
          self.read_link(self.tasks[actions[1]].link)
    else:
      print(f"{cmd} não processado")
      input("Digite enter para continuar")

  def show_help(self):
    print("Digite " + red("t") + " os números ou intervalo das tarefas para (marcar/desmarcar), exemplo:")
    print(green("play $ ") + "t 1 3-5")
    input()

  def show_header(self):
      self.clear()
      ball    = self.show_done and self.show_init and self.show_todo
      show_ajuda = "Digite " + red("c") + " ou " + red("cmds") + " para " + yellow("ocultar") + " a ajuda "
      hide_ajuda = "Digite " + red("c") + " ou " + red("cmds") + " para " +  green("mostrar") + " a ajuda" 
      vall    = (green(GSym.vcheck) if     ball                    else yellow(GSym.vuncheck)) + red("all")
      vdone   = (green(GSym.vcheck) if not ball and self.show_done else yellow(GSym.vuncheck)) + red("done")
      vinit   = (green(GSym.vcheck) if not ball and self.show_init else yellow(GSym.vuncheck)) + red("init")
      vtodo   = (green(GSym.vcheck) if not ball and self.show_todo else yellow(GSym.vuncheck)) + red("todo")
      vlink   = (green(GSym.vcheck) if self.show_link              else yellow(GSym.vuncheck)) + red("link")
      vperc   = (green(GSym.vcheck) if self.show_perc              else yellow(GSym.vuncheck)) + red("perc")
      nomes_verm = green("Os nomes em vermelho são comandos")
      prime_letr = green("Digite o comando ou a primeira letra")
      numeros = red("<Número>") + cyan(" {3 5-8} ") + yellow("(expandir/contrair)")
      sair = red("help ") + red("quit ")
      todas = red("{") + " ou " + red("}") + yellow(" (expandir/contrair) ") + "TUDO"
      letras  = red("<Letra>") + cyan("  {A C-E}") + yellow(" (marcar/desmarcar)")
      graduar =  red("<Letra><Valor>")  + colour("c", " {B0 A9}") + yellow(" (dar nota)")
      read = red("read <Letra>") + cyan(" {r B}") + yellow(" (ler)")
      down = red("down <Letra>") + cyan(" {d B}") + yellow(" (baixar)")

      indicadores = f"{vall} {vdone} {vinit} {vtodo} {vlink} {vperc}"

      term_size = shutil.get_terminal_size().columns
      limit = 75
      token = "\n" if term_size < limit else " ║ "

      if not self.show_cmds:
        print(hide_ajuda + token + indicadores)
      else:
        print(show_ajuda + token + indicadores)
        print(nomes_verm + "     " + token + prime_letr)
        print(numeros + "  " + token + todas)
        print(letras + "   " + token + graduar)
        print(down + "           " + token + read + " ║ " + sair)

      self.show_tasks()
      print("\n" + green("play$") + " ", end="")

  def play(self):
    while True:
      self.show_header()
      line = input()
      if line != "" and "quit".startswith(line):
        break
      actions = self.expand_range(line)
      self.take_actions(actions)
      self.save_to_json()
