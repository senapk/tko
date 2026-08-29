from __future__ import annotations
from tko.game.task import Task
from tko.game.task_config import TaskConfig
from tko.game.task_location import TaskLocation
from tko.game.task_matcher import TaskMatcher
from tko.util.git_hub_url import GitHubUrl
from tko.i18n import Msg
from icecream import ic # type: ignore
from pathlib import Path



_TASK_PARSER_VIEW_EXTERNAL_URL = Msg.text(
    pt="Parseando tarefa de leitura com URL externa: {url}",
    en="Parsing read task with external url: {url}",
)
_TASK_PARSER_EDIT_EXTERNAL_URL = Msg.text(
    pt="Parseando tarefa de execução com URL externa: {url}",
    en="Parsing do task with external url: {url}",
)

class TaskParser:
    """
    Faz o parsing de linhas de tarefas no formato markdown, suportando tanto o modelo chave-valor quanto o modelo antigo.

    Formato canônico (chave-valor):
        - [ ] `@t1 gain=10 hard=3 size=2 type=make eval=test` [Título](t1/README.md)
        - [ ] `@t2 gain=5 type=read` [Material](https://exemplo.com/material)

    Campos suportados:
        - @chave: identificador único da task
        - gain=valor: utilidade / valor da tarefa (antigo xp)
        - hard=valor: nível de dificuldade da tarefa (1-4, antigo tier)
        - size=valor: tamanho / extensão da tarefa
        - type=make ou type=read: tipo da tarefa (produção de código ou consumo de leitura)
        - eval=test ou eval=self: modo de avaliação (test: testes automáticos, self: autoavaliação)

    Valores padrão:
        - gain: 1
        - hard: 1
        - size: 1
        - type: make
        - eval: test para type=make, self para type=read

    Notas:
        - Apenas @chave é obrigatória.
        - Campos não obrigatórios assumem valores padrão.
        - Sintaxe antiga (:15, :make, :read, :test, :self, xp=, tier=) ainda é suportada por compatibilidade.
        - Para links externos http/https: URLs normais funcionam como leitura ou execução externa; URLs do GitHub são tratadas como tarefas remotas importáveis.

    Exemplos:
        - [ ] `@t1  gain=8 hard=1 size=1 type=make eval=test` [Implementar soma](t1/README.md)
        - [ ] `@t2  gain=5 type=read`                        [Ler artigo](https://exemplo.com/material)
        - [ ] `@foo gain=9 hard=2 size=2`                    [Tarefa de exemplo](exemplo/README.md)
        - [ ] `@bar type=read`                               [Material externo](https://exemplo.com/material)
    """

    def __init__(self, index_path: Path, remote_import: bool = False):
        self.index_path = index_path
        self.task: Task = Task()
        self.remote_import = remote_import

    def __remove_tags_from_title(self, text: str) -> str:
        """
        Remove tags (prefixos começando com : ou @) do título extraído do índice.
        Exemplo: ':read @foo Título' -> 'Título'
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

        task.game.gain = tm.gain
        task.game.hard = tm.hard
        task.game.size = tm.size
        task.config = TaskConfig(test=tm.eval)
        task.basic.title = self.__remove_tags_from_title(tm.title)

        if task.basic.key == "":
            return None
 
        task.location = TaskLocation(
            index_path=self.index_path,
            raw_link=tm.link,
            line_number=line_num,
            line_data=line,
            task_type=tm.resource_type,
            git_hub_url=GitHubUrl.parse(tm.link) if tm.is_make else None,
            remote_import=self.remote_import if tm.is_make else False,
        )

        return task
