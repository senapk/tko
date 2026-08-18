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

    Formato recomendado (chave-valor):
        - [ ] `@t1 xp=10 tier=3 type=make eval=test loss=part` [Título](t1/README.md)
        - [ ] `@t2 xp=5 type=read` [Material](https://exemplo.com/material)

    Campos suportados:
        - @chave: identificador único da task
        - xp=valor: valor em pontos/XP da tarefa
        - tier=valor: nível de dificuldade da tarefa
        - type=make ou type=read: tipo da tarefa (produção ou consumo)
        - eval=test ou eval=self: modo de avaliação (test: automática por testes, self: autoavaliação)
        - loss=zero, loss=part, loss=free: política de penalidade por consulta (zero: perde tudo, part: perde parte, free: sem penalidade)

    Valores padrão:
        - type: make
        - eval: test para tarefas de produção, self para tarefas de consumo
        - loss: part para tarefas de produção, free para tarefas de consumo
        - xp: 1
        - tier: 1

    Notas:
        - Apenas @chave é obrigatória.
        - Campos podem aparecer antes do link, no título ou depois do link.
        - Campos não obrigatórios assumem valores padrão.
        - Sintaxe antiga (:15, :make, :read, :test, :self, :zero, :part, :free) ainda é suportada por compatibilidade.
        - Para links externos http/https: type=read vira URL externa; type=make aceita URLs do GitHub e converte outras URLs externas para leitura.

    Exemplos:
        - [ ] `@t1  xp=8 tier=1 type=make loss=part` [Implementar soma](t1/README.md)
        - [ ] `@t2  xp=5 tier=1 type=read          ` [Ler artigo](https://exemplo.com/material)
        - [ ] `@foo xp=9 tier=1 type=make loss=zero` [Tarefa de exemplo](exemplo/README.md)
        - [ ] `@bar xp=1 tier=1 type=read          ` [Material externo](https://exemplo.com/material)
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

        task.game.xp = tm.xp
        task.game.tier = tm.tier
        task.config = TaskConfig(test=tm.eval, loss=tm.loss)
        task.basic.title = self.__remove_tags_from_title(tm.title)

        if task.basic.key == "":
            return None
 
        task.location = TaskLocation(
            index_path=self.index_path,
            raw_link=tm.link,
            line_number=line_num,
            line_data=line,
            task_type=tm.resource_type,
            git_hub_url=GitHubUrl.parse(tm.link),
            remote_import=self.remote_import
        )

        return task
