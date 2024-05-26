#!/usr/bin/env python3

import argparse
import subprocess
import re
from typing import Optional
import os
import shutil


class Color:
  map = {
      "red": '\u001b[31m',
      "green": '\u001b[32m',
      "yellow": '\u001b[33m',
      "blue": '\u001b[34m',
      "magenta": '\u001b[35m',
      "cyan": '\u001b[36m',
      "white": '\u001b[37m',
      "reset": '\u001b[0m',
      "bold": '\u001b[1m',
      "uline": '\u001b[4m'
  }

  @staticmethod
  def ljust(text: str, width: int) -> str:
    return text + ' ' * (width - Color.len(text))

  @staticmethod
  def center(text: str, width: int, filler: str) -> str:
    return filler * ((width - Color.len(text)) // 2) + text + filler * (
        (width - Color.len(text) + 1) // 2)

  @staticmethod
  def remove_colors(text: str) -> str:
    for color in Color.__map.values():
      text = text.replace(color, '')
    return text

  @staticmethod
  def len(text):
    return len(Color.remove_colors(text))

def colour(text: str, color: str="green", color2: Optional[str] = None) -> str:
  return (Color.map[color] + ("" if color2 is None else Color.map[color2]) + text + Color.map["reset"])

class Task:

  def __init__(self):
    self.line_number = 0
    self.line = ""
    self.key = ""
    self.coding = False
    self.remove_tko = False
    self.done = False
    self.skills = []
    self.title = ""
    self.link = ""

  def __str__(self):
    return f"{self.line_number} : {self.key} : {self.done} : {self.title} : {self.skills} : {self.link}"

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

  def process_link(self, baseurl):
    if self.link.startswith("http"):
      return
    if self.link.startswith("./"):
      self.link = self.link[2:]
    self.link = baseurl + self.link

  def parse_task(self, line, line_num):
    if line == "":
      return False
    line = line.lstrip()
    # if not line.startswith("- [ ]") and not line.startswith("- [x]"):
    #   return False

    titulo, link, html = Task.parse_titulo_link_html(line)

    if titulo is None:
      return False

    self.line = line
    self.line_number = line_num
    self.title = titulo
    self.link = link

    self.process_link(link)

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
    self.requires = []
    self.requires_ptr = []
    self.type = "main"

  def __str__(self):
    return f"linha={self.line_number} : {self.key} : {self.title} : {self.skills} : {self.requires} : {self.mdlink} : {[t.key for t in self.tasks]}"

  def is_complete(self):
    return all([t.done for t in self.tasks])

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


# class Rep:

#   default_filename = ".game.json"

#   def __init__(self):
#     self.from_file = ""
#     self.from_url = ""
#     self.active_quests: List[str] = []
#     self.done_tasks: List[str] = []
#     self.show_url = False
#     self.show_done = False

#   # recursivamente vai retornando no caminho de diretórios procurando o arquivo .tko_game.json
#   @staticmethod
#   def search_for_json(folder):
#     if os.path.exists(folder + "/" + Rep.default_filename):
#       return folder + "/" + Rep.default_filename
#     if folder == "/":
#       return None
#     return Rep.search_for_json(os.path.dirname(folder))

#   def save_to_json(self, json_file):
#     with open(json_file, "w") as f:
#       json.dump(self, f, default=lambda o: o.__dict__, indent=4)

#   def set_file(self, file):
#     self.from_file = os.path.abspath(file)

#   def get_file(self):
#     return self.from_file

#   def load_from_json(self, json_file):
#     with open(json_file, "r") as f:
#       data = json.load(f)
#       self.from_file = data["from_file"]
#       self.from_url = data["from_url"]
#       self.active_quests = data["active_quests"]
#       self.done_tasks = data["done_tasks"]
#       self.show_url = data["show_url"]
#       self.show_done = data["show_done"]

#   def __str__(self):
#     return f"from_file={self.from_file} : from_url={self.from_url} : active_quests={self.active_quests} : done_tasks={self.done_tasks}"


class Game:

  def __init__(self):
    self.quests = {}
    self.tasks = {}

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
    print("debug a")
    valid_quests = {}
    for k, q in self.quests.items():
      if len(q.tasks) > 0:
        valid_quests[k] = q

    self.quests = valid_quests

    print("debug b")
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

  def get_reachable_quests(self):
    # cache needs to be reseted before each call
    cache = {}
    return [q for q in self.quests.values() if q.is_reachable(cache)]

  def show_quests(self):
    print( f"Quests de Entrada: {[q.key for q in self.quests.values() if len(q.requires) == 0]}" )
    print(f"Total de quests: {len(self.quests)}")
    print("\n".join([str(q) for q in self.quests.values()]))


class Play:

  def __init__(self, game: Game, rep, fnsave):
    self.fnsave = fnsave
    self.rep = rep
    self.show_url = self.rep.show_url
    self.show_done = self.rep.show_done
    self.game = game
    self.tasks = []
    self.quests = {}  # option:quest
    self.active = set(self.rep.active_quests)
    self.term_limit = 130

    for t in game.tasks.values():
      if t.key in self.rep.done_tasks:
        t.done = True

  def save_to_json(self):
    self.rep.active_quests = list(self.active)
    self.rep.done_tasks = [t.key for t in self.game.tasks.values() if t.done]
    self.rep.show_url = self.show_url
    self.rep.show_done = self.show_done
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
      index_letter = 0
      for q in quests:
        letter = self.calc_letter(index_letter)
        self.quests[letter] = q
        index_letter += 1
    else:
      index_letter = len(self.quests.keys())
      for q in quests:
        if q.key not in menu_keys:
          letter = self.calc_letter(index_letter)
          self.quests[letter] = q
          index_letter += 1

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


  def print_quest(self, entry, q, max_title, term_size):
    resume = ""
    opening = "➡️"
    if q.key in self.active:
      opening = "⬇️"
    done = len([t for t in q.tasks if t.done])
    size = len(q.tasks)
    if done > 9:
      done = "*"
    if size > 9:
      size = "*"
    text = f"[{str(done)}/{str(size)}]"
    space = " " if len(entry) == 1 else ""
    if done == size:
      resume = colour(text, "green")
    elif done == 0:
      resume = colour(text, "red")
    else:
      resume = colour(text, "yellow")
    entry = colour(entry, "blue") if q.type == "main" else colour(entry, "magenta")
    qlink = ""
    if self.show_url:
      if term_size > self.term_limit:
        qlink = " " + colour(q.mdlink, "cyan")
      else:
        qlink = "\n      " + colour(q.mdlink, "cyan")
    if not self.show_done and done == size:
      return
    print(f"{opening} {entry}{space}{resume} {q.title.ljust(max_title)}")

  def print_task(self, t, max_title, index, term_size):
    vindex = str(index).rjust(2, "0")
    vdone = "x" if t.done else " "
    vlink = ""
    if self.show_url:
      if t.key in t.title:
        vlink = colour(t.link, "red")
      else:
        vlink = colour(t.link, "yellow")
      if term_size > self.term_limit:
        vlink = " " + vlink
      else:
        vlink = "\n      " + vlink
    print(f"  {vindex} [{vdone}] {t.title.strip().ljust(max_title + 1)}{vlink}")

  def sort_keys(self, keys):
    single = [k for k in keys if len(k) == 1]
    double = [k for k in keys if len(k) == 2]
    return sorted(single) + sorted(double)

  def show_tasks(self):
    term_size = shutil.get_terminal_size().columns
    self.tasks = []

    self.update_reachable()
    max_title = self.calculate_pad()
    index = 0
    for entry in self.sort_keys(self.quests.keys()):
      q = self.quests[entry]
      self.print_quest(entry, q, max_title, term_size)
      if q.key not in self.active:
        continue
      if not self.show_done and q.is_complete():
        continue
      for t in q.tasks:
        self.print_task(t, max_title, index, term_size)
        index += 1
        self.tasks.append(t)

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

  def expand_range(self, line):
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

  def take_actions(self, actions):
    for t in actions:
      if t == ":h" or t == ":help" or t == "?":
        subprocess.run("clear")
        self.show_help()
      elif t == ":u" or t == ":url":
        self.show_url = not self.show_url
      elif t == ":a" or t == ":all":
        self.show_done = not self.show_done
      elif t == "<":
        self.active = set()
      elif t == ">":
        self.update_reachable()
        self.active = set([q.key for q in self.quests.values()])
      else:
        try:  # number
          t = int(t)
          if t >= 0 and t < len(self.tasks):
            self.tasks[t].done = not self.tasks[t].done
        except:  # letter
          t = t.upper()
          if t in self.quests:
            key = self.quests[t].key
            if key not in self.active:
              self.active.add(key)
            else:
              self.active.remove(key)
          else:
            print(f"{t} não processado")

  def show_help(self):
    print("Digite os números ou intervalo das tarefas para (marcar/desmarcar), exemplo:")
    print(colour("$ ", "green") + "1 2 5-6")
    print("Digite as letras ou intervalo das quests para (expandir/colapsar), exemplo:")
    print(colour("$ ", "green") + "a c d-g")
    print("Digite > para expandir todas as quests")
    print(colour("$ ", "green") + ">")
    print("Digite < para colapsar todas as quests")
    print(colour("$ ", "green") + "<")
    print("Digite :a ou :all para mostrar/esconder as quests completas")
    print(colour("$ ", "green") + ":all")
    print("Digite :u ou :url para mostrar/esconder as urls")
    print(colour("$ ", "green") + ":url")
    print("Digite :h ou :help para mostrar a ajuda")
    print(colour("$ ", "green") + ":h")
    print("Digite :q ou :quit para sair")
    print(colour("$ ", "green") + ":q")
    print("Digite enter para continuar")
    input()

  def play(self):
    while True:
      subprocess.run("clear")
      vnum = colour("números") + "(marcar)"
      vlet = colour("letras") + "(expandir)"
      vfold  = colour("<") + " ou " + colour(">") + "(expandir todas)"
      vhelp  = colour(":h", "cyan") + colour("elp")
      vclose = colour(":q", "cyan") + colour("uit")
      vdone  = colour(":d", "cyan") + colour("one") + ("[x]" if self.show_done else "[ ]")
      vinit  = colour(":i", "cyan") + colour("nit") + ("[x]" if self.show_done else "[ ]")
      vtodo  = colour(":t", "cyan") + colour("odo") + ("[x]" if self.show_done else "[ ]") 
      vlink   = colour(":l", "cyan") + colour("ink") + ("[x]" if self.show_url else "[ ]")
      print(f"Digite: {vnum}, {vlet}, {vfold}, {vhelp} ou {vclose}.")
      print(f"Filtro: {vdone}, {vinit}, {vtodo}, {vlink}, {vlink}")
      self.show_tasks()
      print("\n" + colour("$") + " ", end="")
      line = input()
      if ":q" in line or ":quit" in line:
        break
      actions = self.expand_range(line)
      self.take_actions(actions)
      self.save_to_json()


def create_diag(quests, output, colors=None):
  saida = []
  saida.append(f"@startuml {output}")
  saida.append("skinparam defaultFontName Hasklig")
  # saida.append("skinparam defaulttextalignment left")

  # links  = " [[https://raw.githubusercontent.com/senapk/c_is_fun/main/graph/full_data.svg full_data]]"
  # links += " [[https://raw.githubusercontent.com/senapk/c_is_fun/main/graph/main_only.svg main_only]]"
  # links += " [[https://raw.githubusercontent.com/senapk/c_is_fun/main/graph/main_side.svg main_side]]"
  # links += " [[https://raw.githubusercontent.com/senapk/c_is_fun/main/graph/main_game.svg main_game]]"

  # saida.append("header")
  # saida.append("C is Fun links: " + links)
  # saida.append("end header")
  #saida.append("left to right direction")

  def info(q):
    color = "lime" if q.type == "main" else "yellow"
    return f"\"{q.title.strip()}:{len(q.tasks)}\" #{color}"

  for q in quests.values():
    token = "-->"
    if len(q.requires_ptr) > 0:
      for r in q.requires_ptr:
        saida.append(f"{info(r)} {token} {info(q)}")
    else:
      saida.append(f"{"Início"} #cyan {token} {info(q)}")

  saida.append(f"{info(list(quests.values())[-1])} --> (*)")

  # skills = {}
  # for e in entries:
  #     for s, v in e.skills:
  #         if s not in skills:
  #             skills[s] = v
  #         else:
  #             skills[s] += v

  # saida.append("legend bottom left")

  # for s in skills:
  #     name = s.rjust(7, ".")
  #     print(name)
  #     saida.append(f"  {name}: {skills[s]}")
  # saida.append("end legend")

  # saida.append("note top right")
  # saida.append("    full_data: [[https://raw.githubusercontent.com/senapk/c_is_fun/main/graph/full_data.svg LINK]]")
  # saida.append("    main_only: [[https://raw.githubusercontent.com/senapk/c_is_fun/main/graph/main_only.svg LINK]]")
  # saida.append("    main_side: [[https://raw.githubusercontent.com/senapk/c_is_fun/main/graph/main_side.svg LINK]]")
  # saida.append("    main_game: [[https://raw.githubusercontent.com/senapk/c_is_fun/main/graph/main_game.svg LINK]]")
  # saida.append("end note")

  saida.append("@enduml")
  saida.append("")

  open(output + ".puml", "w").write("\n".join(saida))
  subprocess.run(["plantuml", output + ".puml", "-tsvg"])

class Main:
  @staticmethod
  def init(args):
    if args.url is None and args.file is None and args.rep is None:
      print("Você precisa definir a fonte do seu jogo.")
      exit(1)
    if args.url:
      rep = Rep()
      rep.from_url = args.url
      rep.save_to_json()
      return
    if args.file:
      rep = Rep()
      rep.set_file(args.file)
      rep.save_to_json(Rep.default_filename)
      return

  @staticmethod
  def play(args):
    rep = Rep()
    json_file = rep.search_for_json(os.getcwd())
    if json_file is None:
      print("Arquivo .game.json não encontrado")
      exit(1)
    rep.load_from_json(json_file)

    game = Game()
    game.parse_file(rep.get_file())

    play = Play(game, rep, json_file)
    play.play()

  @staticmethod
  def diag(args):
    rep = Rep()
    json_file = rep.search_for_json(os.getcwd())
    if json_file is None:
      print("Arquivo .game.json não encontrado")
      exit(1)
    rep.load_from_json(json_file)

    game = Game()
    game.parse_file(rep.get_file())
    game.check_cycle()
    create_diag(game.quests, "graph", None)

    print("Diagrama gerado em graph.puml")

def main():

  parser = argparse.ArgumentParser()
  # subcommand
  subparsers = parser.add_subparsers(dest="subcommand")

  parser_init = subparsers.add_parser('init')
  parser_init.add_argument("--url", "-u", type=str, help="Inicia um jogo na pasta atual passando a url")
  parser_init.add_argument("--file", "-f", type=str, help="Inicia um jogo na pasta atual passando a url")
  parser_init.set_defaults(func=Main.init)

  parser_play = subparsers.add_parser('play')
  parser_play.set_defaults(func=Main.play)

  parser_diag = subparsers.add_parser('diag')
  parser_diag.set_defaults(func=Main.diag)

  args = parser.parse_args()

  if "func" in args:
    args.func(args)
  else:
    parser.print_help()

if __name__ == "__main__":
  main()
