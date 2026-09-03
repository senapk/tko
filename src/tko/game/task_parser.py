from __future__ import annotations
from tko.game.task import Task
from tko.game.task_config import TaskConfig
from tko.game.task_location import TaskLocation
from tko.game.task_matcher import TaskMatcher
from tko.util.git_hub_url import GitHubUrl
from tko.i18n import Msg
from icecream import ic # type: ignore
from pathlib import Path
from urllib.parse import urlparse



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
        - [ ] `@t1 type=make gain=10 hard=3 size=2 eval=test` [Título](t1/README.md)
        - [ ] `@t2 gain=5 type=read` [Material](wiki/material/README.md)

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
        - Para links locais, @chave é derivada do caminho relativo ao índice.
        - Para links externos, @chave explícita é obrigatória.
        - Campos não obrigatórios assumem valores padrão.
        - Sintaxe antiga (:15, :make, :read, :test, :self, xp=, tier=) ainda é suportada por compatibilidade.
        - Links externos devem ser URLs do GitHub apontando para um README.md; eles são tratados como tarefas remotas importáveis.

    Exemplos:
        - [ ] `@t1  type=make gain=8 hard=1 size=1 eval=test` [Implementar soma](t1/README.md)
        - [ ] `@t2  gain=5 type=read`                        [Ler material](wiki/material/README.md)
        - [ ] `@foo gain=9 hard=2 size=2`                    [Tarefa de exemplo](exemplo/README.md)
        - [ ] `@bar type=read`                               [Material externo](https://github.com/user/repo/blob/main/wiki/material/README.md)
    """

    def __init__(self, index_path: Path, external_source: bool = False):
        self.index_path = index_path
        self.task: Task = Task()
        self.external_source = external_source

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
        elif not tm.is_url and Path(tm.link).name == "README.md":
            link_path = Path(tm.link)
            if link_path.is_absolute():
                link_path = link_path.resolve()
            else:
                link_path = (self.index_path.parent / link_path).resolve()
            try:
                task.basic.key = link_path.parent.relative_to(self.index_path.parent.resolve()).as_posix()
            except ValueError:
                task.basic.key = ""

        task.game.gain = tm.gain
        task.game.hard = tm.hard
        task.game.size = tm.size
        task.config = TaskConfig(test=tm.eval)
        task.basic.title = self.__remove_tags_from_title(tm.title)

        if task.basic.key == "" or (tm.is_url and tm.key is None):
            return None

        TaskMatcher.validate_key(task.basic.key)
        self.__validate_task_link(tm.link)
 
        task.location = TaskLocation(
            index_path=self.index_path,
            raw_link=tm.link,
            line_number=line_num,
            line_data=line,
            task_type=tm.resource_type,
            git_hub_url=GitHubUrl.parse(tm.link),
            external_source=self.external_source,
        )

        return task

    @staticmethod
    def __validate_task_link(link: str) -> None:
        parsed = urlparse(link)
        if parsed.scheme in {"http", "https"}:
            github = GitHubUrl.parse(link)
            if github is None or not parsed.netloc.lower() in {"github.com", "www.github.com"}:
                raise ValueError(
                    f"Task must point to a local README.md or a GitHub README.md: {link}"
                )
            if "/blob/" not in parsed.path or not parsed.path.rstrip("/").endswith("/README.md"):
                raise ValueError(
                    f"Task GitHub link must point to a README.md file: {link}"
                )
            return

        if Path(link).name != "README.md":
            raise ValueError(f"Task activity must point to a README file: {link}")
