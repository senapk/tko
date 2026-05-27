from __future__ import annotations
import logging
from tko.game.task import Task
from tko.game.task_enums import TaskType
from tko.game.task_matcher import TaskMatcher
from tko.feno.github_url_structure import GithubUrlStructure
from tko.i18n import Msg
from icecream import ic # type: ignore
from pathlib import Path


logger = logging.getLogger(__name__)

_TASK_PARSER_VIEW_EXTERNAL_URL = Msg(
    pt="Parseando tarefa de leitura com URL externa: {url}",
    en="Parsing read task with external url: {url}",
)
_TASK_PARSER_EDIT_EXTERNAL_URL = Msg(
    pt="Parseando tarefa de execução com URL externa: {url}",
    en="Parsing do task with external url: {url}",
)



class TaskParser:
    """
    Faz o parsing de linhas de tarefas no formato markdown, suportando tanto o modelo chave-valor quanto o modelo antigo.

    Formato recomendado (chave-valor):
        - [ ] key=@t1 xp=10 type=task path=main eval=test loss=part
        - [ ] @t2 xp=5 type=read path=side eval=self loss=free

    Campos suportados:
        - key=@chave ou @chave: identificador único da task
        - xp=valor: valor em pontos/XP da tarefa
        - tier=valor: nível de dificuldade da tarefa
        - type=task ou type=read: tipo da tarefa (produção ou consumo)
        - path=main ou path=side: categoria/trilha da tarefa
        - eval=test ou eval=self: modo de avaliação (test: automática por testes, self: autoavaliação)
        - loss=zero, loss=part, loss=free: política de penalidade por consulta (zero: perde tudo, part: perde parte, free: sem penalidade)

    Valores padrão:
        - type: task
        - path: main
        - eval: test para tarefas de produção, self para tarefas de consumo
        - loss: part para tarefas de produção, free para tarefas de consumo
        - xp: 1
        - tier: 1

    Notas:
        - Apenas key é obrigatória.
        - Campos podem aparecer em qualquer ordem.
        - Campos não obrigatórios assumem valores padrão.
        - Sintaxe antiga (:main, :side, :test, etc) ainda é suportada por compatibilidade, mas recomenda-se o novo formato.
        - tier vai de 1 até 5

    Exemplos:
        - [ ] key=@t1 xp=10 type=task path=main eval=test loss=part tier=3
        - [ ] @t2 xp=5 type=read path=side eval=self loss=free
        - [ ] @foo :main:free [Tarefa de exemplo](exemplo/README.md)
        - [ ] @bar :side:perk [Outra tarefa](https://exemplo.com/material)
    """

    def __init__(self, index_path: Path, remote_dir_root: Path, remote_name: str, remote_git_url: str | None = None, editable_source: bool = False):
        self.index_path = index_path
        self.task: Task = Task()
        self.task.basic.remote_name = remote_name
        self.editable_source = editable_source
        self.remote_dir = remote_dir_root
        self.remote_url = remote_git_url

    
    def __remove_tags_from_title(self, text: str) -> str:
        """
        Remove tags (prefixos começando com : ou @) do título extraído do índice.
        Exemplo: ':main @foo Título' -> 'Título'
        """
        words: list[str] = [w for w in text.split()]
        output: list[str] = []
        for item in words:
            if TaskMatcher.is_field(item):
                continue
            output.append(item)
        return " ".join(output)

    def redirect_from_readme(self, link: str) -> str:
        """
        Se o link não for absoluto, resolve o caminho relativo ao índice.
        """
        if not Path(link).is_absolute():
            return (self.index_path.parent / link).as_posix()
        return link

    def parse_line(self, line: str, line_num: int = 0) -> Task | None:
        """
        Faz o parsing de uma linha do índice e retorna um objeto Task preenchido.

        Retorna None se a linha não corresponder ao padrão esperado.
        """
        tm = TaskMatcher()
        if not tm.match_pattern(line):
            return None
        task = self.task
        if tm.key is not None:
            task.basic.key = tm.key
        task.resource.line_number = line_num
        task.resource.line_data = line
        task.resource.raw_link = tm.link
        task.resource.task_type = tm.resource_type
        task.game.xp = tm.xp
        task.game.tier = tm.tier
        task.config.test = tm.test
        task.config.loss = tm.loss

        task.basic.title = self.__remove_tags_from_title(tm.title)

        if task.basic.key == "":
            return None

        # url link tasks
        if tm.link.startswith(r"http://") or tm.link.startswith(r"https://"):
            if task.resource.is_read:
                # logger.info(t(_TASK_PARSER_VIEW_EXTERNAL_URL, url=tm.link))
                self.task.resource.external_url = tm.link
                return self.task
            else:
                parser = GithubUrlStructure()
                if parser.parse(tm.link):
                    task.resource.remote_git = parser.repository_url
                    task.resource.remote_dir = self.remote_dir
                    task.resource.relative_path = Path(parser.relative_path)
                    task.resource.editable_source = False
                    return task
                else:
                    # logger.warning(t(_TASK_PARSER_EDIT_EXTERNAL_URL, url=tm.link))
                    task.resource.external_url = tm.link
                    task.resource.editable_source = False
                    task.resource.task_type = TaskType.READ
                    return task
        
        # file read, static task or import task
        path = Path(self.redirect_from_readme(tm.link)).resolve()
        task.resource.remote_git = self.remote_url
        task.resource.remote_dir = self.remote_dir
        task.resource.relative_path = path.resolve().relative_to(self.remote_dir.resolve(), walk_up=True)
        task.resource.editable_source = self.editable_source

        return task
    