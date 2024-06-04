
from typing import Dict, List
from .game import Game, Task, Quest
from .settings import RepoSettings
from .remote import RemoteCfg
from .down import Down
from .format import GSym, colour, red, green, yellow, cyan, Color
import subprocess
import shutil
import tempfile
import os
import re


class Play:
  cluster_prefix = "'"

  def __init__(self, game: Game, rep: RepoSettings, repo_alias: str, fnsave):
    self.fnsave = fnsave
    self.repo_alias = repo_alias
    self.rep = rep
    self.show_link = "link" in self.rep.view
    self.show_done = "done" in self.rep.view
    self.show_init = "init" in self.rep.view
    self.show_todo = "todo" in self.rep.view
    self.show_cmds = "cmds" in self.rep.view
    self.show_perc = "perc" in self.rep.view
    self.show_fold = "fold" in self.rep.view
    self.show_hack = "hack" in self.rep.view
    
    if not self.show_done and not self.show_init and not self.show_todo:
      self.show_done = True
      self.show_init = True
      self.show_todo = True

    self.game: Game = game

    self.cluster_view: Dict[str, str] = {}
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
  
  def down_task(self, task: Task):
    if task.key in task.title:
      print(f"Tarefa de código {task.key}")
      print(f"Baixando com o comando " + red(f"tko down {self.repo_alias} {task.key}"))
      result = Down.download_problem(self.repo_alias, task.key, None)
      # result = subprocess.run(["tko", "down", self.repo_alias, task.key])
      if result:
        print(f"Tarefa baixada na pasta " + red(f"{os.getcwd()}/{task.key}/Readme.md"))
    else:
      print(f"Essa não é uma tarefa de código")
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
    if self.show_fold:
      self.rep.view.append("fold")
    if self.show_hack:
      self.rep.view.append("hack")
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

    #self.active = set([k for k in self.active if k in reach_keys])

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

  def str_quest(self, entry, q, max_title, term_size) -> str:
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
      text = f"{str(q.get_percent()).rjust(2)}%"
      if q.get_percent() == 100:
        text = GSym.check * 3
    else:
      text = f"{str(done)}/{str(size)}"
    space = " " if len(entry) == 1 else ""
    if q.get_percent() == 100:
      resume = cyan(text)
    elif q.is_complete():
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
      return ""
    title = q.title
    if self.show_link and term_size > self.term_limit:
      title = title.strip().ljust(max_title + 1)
    return f"{space}{entry} {opening} {resume} {title}"

  def str_task(self, t, max_title, letter, term_size) -> str:
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
        vlink = "\n   " + vlink
    return f"  {vindex}  {vdone}  {title}{vlink}"

  def sort_keys(self, keys):
    single = [k for k in keys if len(str(k)) == 1]
    double = [k for k in keys if len(str(k)) == 2]
    return sorted(single) + sorted(double)

  def print_cluster(self, cluster_key, cluster_name: str, lines: List[str]):
    opening = "➡️"
    if cluster_name in self.active:
      opening = "⬇️"
    intro = [Color.remove_colors(l).strip().split(" ")[0] for l in lines]
    quests = [v for v in intro if v.isdigit()]
    total = len(quests)
    init = yellow(str(len([v for v in quests if self.quests[v].in_progress()])))
    done = green(str(len([v for v in quests if self.quests[v].is_complete()])))
    todo = red(str(len([v for v in quests if self.quests[v].not_started()])))
    
    if total > 0:
      print(f"{yellow(cluster_key)} {opening} {done}/{init}/{todo} {cluster_name}")
      if cluster_name in self.active:
        for line in lines:
          print("  " + line)
    
  def show_options(self):
    term_size = shutil.get_terminal_size().columns
    max_title = self.calculate_pad()
    index = 0

    clusters: Dict[str, List[str]] = {}

    for entry in self.sort_keys(self.quests.keys()):
      quest_output: List[str] = []
      q = self.quests[entry]
      quest_output.append(self.str_quest(entry, q, max_title, term_size))
      if q.key in self.active and self.to_show_quest(q):
        for t in q.tasks:
          letter = self.calc_letter(index)
          quest_output.append(self.str_task(t, max_title, letter, term_size))
          index += 1
          self.tasks[letter] = t
      
      if self.show_fold:
        if len(quest_output) > 0:
          if q.group not in clusters:
            clusters[q.group] = []
          clusters[q.group] += [line for line in quest_output if line != ""]
      else:
        for line in quest_output:
          if line != "":
            print("  " + line)

    if self.show_fold:
      cluster_index = 1
      for group in self.game.cluster_order:
        if group in clusters.keys():
          key = Play.cluster_prefix + str(cluster_index)
          self.cluster_view[key] = group
          self.print_cluster(key, group, clusters[group])
          cluster_index += 1
    return

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

    if cmd == "<":
      all_tasks_closed = True
      for v in self.active:
        if v not in self.cluster_view.values():
          all_tasks_closed = False
          break
      if all_tasks_closed:
        self.active = []
      else:
        self.active = [q for q in self.active if q in self.cluster_view.values()]
    elif cmd == ">":
      self.update_reachable()
      # verify if all clusters are expanded
      all_clusters_expanded = True
      for k in self.cluster_view.values():
        if k not in self.active:
          all_clusters_expanded = False
          break
      if all_clusters_expanded:
        self.active = [q.key for q in self.quests.values()] + [k for k in self.cluster_view.values()]
      else:
        self.active = self.active + [k for k in self.cluster_view.values()]
      
    elif cmd == "m" or cmd == "man":
      self.clear()
      self.show_help()
    elif cmd == "h" or cmd == "help":
      self.show_cmds = not self.show_cmds
    elif cmd == "a" or cmd == "all":
      self.show_done = True
      self.show_init = True
      self.show_todo = True
    elif cmd == "i" or cmd == "init":
      self.show_done = False
      self.show_init = True
      self.show_todo = False
    elif cmd == "d" or cmd == "done":
      self.show_done = True
      self.show_init = False
      self.show_todo = False
    elif cmd == "t" or cmd == "todo":
      self.show_todo = not self.show_todo
    elif cmd == "l" or cmd == "link":
      self.show_link = not self.show_link
    elif cmd == "p" or cmd == "percent":
      self.show_perc = not self.show_perc
    elif cmd == "f" or cmd == "fold":
      self.show_fold = not self.show_fold
    elif cmd == "h" or cmd == "hack":
      self.show_hack = not self.show_hack
    elif cmd == "g" or cmd == "get":
      for t in actions[1:]:
        if t in self.tasks:
          self.down_task(self.tasks[t])
        else:
          print(f"Tarefa {t} não encontrada")
          input()
    elif cmd.startswith(Play.cluster_prefix):
      for t in actions:
        if t in self.cluster_view:
          key = self.cluster_view[t]
          if key not in self.active:
            print(f"Expandindo {key}")
            self.active.append(key)
          else:
            print(f"Contraindo {key}")
            self.active.remove(key)
        else:
          print(f"{t} não processado")
          input("Digite enter para continuar")
    elif self.is_number(cmd):
      for t in actions:
        if self.is_number(t):
          if t in self.quests:
            key = self.quests[t].key
            if key not in self.active:
              self.active.append(key)
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
          # print(self.tasks[actions[1]].link)
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
      show_ajuda = "Digite " + red("h") + " ou " + red("help") + " para " + yellow("ocultar") + " a ajuda"
      hide_ajuda = "Digite " + red("h") + " ou " + red("help") + " para " +  green("mostrar") + " a ajuda" 

      full_count = len([q for q in self.quests.values()])
      done_count = len([q for q in self.quests.values() if q.is_complete()])
      init_count = len([q for q in self.quests.values() if q.in_progress()])
      todo_count = len([q for q in self.quests.values() if q.not_started()])

      vall    = red("all")      + f"({full_count})" + (green(GSym.vcheck) if     ball                    else yellow(GSym.vuncheck))
      vdone   = red("done") + f"({done_count})" + (green(GSym.vcheck) if not ball and self.show_done else yellow(GSym.vuncheck))
      vinit   = red("init")  + f"({init_count})" + (green(GSym.vcheck) if not ball and self.show_init else yellow(GSym.vuncheck))
      vtodo   = red("todo")     + f"({todo_count})" + (green(GSym.vcheck) if not ball and self.show_todo else yellow(GSym.vuncheck))
      vlink   = red("link")     + (green(GSym.vcheck) if self.show_link              else yellow(GSym.vuncheck))
      vperc   = red("percent")  + (green(GSym.vcheck) if self.show_perc              else yellow(GSym.vuncheck)) 
      vjoin   = red("fold")     + (green(GSym.vcheck) if self.show_fold              else yellow(GSym.vuncheck)) 
      vhack   = red("hack")     + (green(GSym.vcheck) if self.show_hack              else yellow(GSym.vuncheck)) 

      nomes_verm = green("    Os nomes em vermelho são comandos")
      prime_letr = green(" A primeira letra do cmd é suficiente")
      numeros = red("<Número>") + cyan(" {3 5-8} ") + yellow("(Expandir/Contrair)")
      todas = red("<") + " ou " + red(">") + yellow("       (Expandir/Contrair) ") + "TUDO"
      letras  = red("<Letra>") + cyan("  {A C-E}") + yellow("   (Marcar/Desmarcar)")
      graduar =  red("<Letra><Valor>")  + colour("c", " {B0 A9}") + yellow(" (Dar nota)")
      read = red("read <Letra>") + cyan(" {r B}") + yellow("  (Ler no terminal)")
      down = red("get <Letra>") + cyan(" {d B}") + yellow("    (Baixar tarefa)")
      manu = red("manual") + yellow("     (Mostrar manual detalhado)")
      sair = red("quit") + yellow("               (Sair do programa)")
                                     
      fold = red("fold") + yellow(" (Mostrar categorias)")
      link = red("link") + yellow("      (Mostrar links das tarefas)")
      hack = red("hack") + yellow(" (Desabilita o modo jogo)")
      perc = red("percent") + yellow("        (Mostrar porcentagens)")

      indicadores = f"{vall} {vdone} {vinit} {vtodo}"
      visoes = f"{vjoin} {vlink} {vperc} {vhack}"

      elementos = []
      if not self.show_cmds:
        elementos = [hide_ajuda, indicadores, visoes]
      else:
        elementos = [show_ajuda, indicadores, visoes, nomes_verm, prime_letr, numeros, todas, letras, graduar,
                     down, read, fold, perc, link, hack, manu, sair]
      self.print_elementos(elementos)

  def print_elementos(self, elementos):
    term_size = shutil.get_terminal_size().columns
    maxlen = max([len(Color.remove_colors(t)) for t in elementos])
    qtd = term_size // (maxlen + 3)
    print(f"debug {maxlen} {qtd}")

    count = 0
    for i in range(len(elementos)):  
      print(Color.ljust(elementos[i], maxlen), end = "")
      count += 1
      if count >= qtd:
        count = 0
        print("")
      else:
        print(" ║ ", end="")
    print("")


  def play(self):
    while True:
      self.tasks = {}
      self.update_reachable()
      self.show_header()
      self.show_options()
      print("\n" + green("play$") + " ", end="")
      line = input()
      if line != "" and "quit".startswith(line):
        break
      actions = self.expand_range(line)
      self.take_actions(actions)
      self.save_to_json()
