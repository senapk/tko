from __future__ import annotations
from tko.game.task import Task
from tko.game.task_config import TaskConfig
from tko.game.task_location import TaskLocation
from tko.game.task_matcher import TaskMatcher
from tko.game.source_xp_config import SourceXpConfig
from tko.util.git_hub_url import GitHubUrl
from tko.feno.task_source import activity_path_from_local_link
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
    Parses Markdown task lines using the source's optional XP configuration.

    A configured source supplies the variable names and formula in its leading YAML
    front matter. Variables are transient: this parser stores only the resulting XP.

    `eval=none` remains XP-free and does not need variables. An unconfigured
    source assigns the default one XP to every evaluable task.
    """

    def __init__(self, index_path: Path, external_source: bool = False, xp_config: SourceXpConfig | None = None):
        self.index_path = index_path
        self.task: Task = Task()
        self.external_source = external_source
        self.xp_config = xp_config or SourceXpConfig(index_path=index_path)

    def __remove_tags_from_title(self, text: str) -> str:
        """
        Remove campos de configuração do título extraído do índice.
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
        tm = TaskMatcher(self.xp_config)
        try:
            if not tm.match_pattern(line):
                return None
        except ValueError as exc:
            source = self.xp_config.source_name or "source"
            raise ValueError(f"{source}:{self.index_path}:{line_num}: {exc}") from exc
        task = self.task
        if tm.is_url:
            # Direct remote links are migration-only. They retain their old
            # explicit key until ``tko index download`` creates a local link.
            task.basic.key = tm.legacy_key or ""
        else:
            try:
                task.basic.key = activity_path_from_local_link(tm.link).as_posix()
            except ValueError:
                task.basic.key = ""

        task.is_reference = tm.is_ref
        eval_mode = tm.eval
        if eval_mode is None:
            raise AssertionError("matched task is missing its evaluation mode")
        task.config = TaskConfig(eval=eval_mode)
        task.basic.title = self.__remove_tags_from_title(tm.title)

        if task.basic.key == "":
            return None

        TaskMatcher.validate_key(task.basic.key)
        self.__validate_task_link(tm.link)
 
        task.location = TaskLocation(
            index_path=self.index_path,
            raw_link=tm.link,
            line_number=line_num,
            line_data=line,
            eval=eval_mode,
            git_hub_url=GitHubUrl.parse(tm.link),
            external_source=self.external_source,
        )

        if task.config.awards_xp:
            task.game.xp = self.xp_config.calculate(tm.variables, task.basic.key, line_num)
        else:
            task.game.xp = 0.0

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

        activity_path_from_local_link(link)
