from __future__ import annotations
import logging
from tko.game.task import Task
from tko.game.task_config import TaskLoss, TaskMain, TaskTest
from tko.game.task_resource import TaskResource, ResourceType
from tko.game.task_matcher import TaskMatcher
from tko.feno.github_url_structure import GithubUrlStructure
from tko.i18n import Msg, t
from icecream import ic # type: ignore
from pathlib import Path


logger = logging.getLogger(__name__)

_TASK_PARSER_VIEW_EXTERNAL_URL = Msg(
    pt="Parseando tarefa de visualização com URL externa: {url}",
    en="Parsing view task with external url: {url}",
)
_TASK_PARSER_EDIT_EXTERNAL_URL = Msg(
    pt="Parseando tarefa de edição com URL externa: {url}",
    en="Parsing edit task with external url: {url}",
)


class TaskParser:

    def __init__(self, index_path: Path, remote_dir_root: Path, remote_name: str, remote_git_url: str | None = None, editable_source: bool = False):
        self.index_path = index_path
        self.task: Task = Task()
        self.task.basic.remote_name = remote_name
        self.editable_source = editable_source
        self.remote_dir = remote_dir_root
        self.remote_url = remote_git_url

    def decode_task_types(self, info: str):
        self.task.config.loss = TaskLoss.NULL
        self.task.config.test = TaskTest.NULL
        for tag in info.split(":"):
            # if c is digit, set xp
            if tag.isdigit():
                self.task.game.xp = int(tag)
            elif tag == TaskTest.TEST.value:
                self.task.config.test = TaskTest.TEST
            elif tag == TaskTest.SELF.value:
                self.task.config.test = TaskTest.SELF
            elif tag == TaskMain.MAIN.value:
                self.task.config.path = TaskMain.MAIN
            elif tag == TaskMain.SIDE.value:
                self.task.config.path = TaskMain.SIDE
            elif tag == TaskMain.PERK.value:
                self.task.config.path = TaskMain.PERK
            elif tag == TaskLoss.FREE.value:
                self.task.config.loss = TaskLoss.FREE
            elif tag == TaskLoss.PART.value:
                self.task.config.loss = TaskLoss.PART
            elif tag == TaskLoss.ZERO.value:
                self.task.config.loss = TaskLoss.ZERO
            else:
                logger.warning(
                    "Parsing %s:%s, Tipo de tarefa desconhecido: %s",
                    self.index_path,
                    self.task.resource.line_number,
                    tag,
                )

    def __parse_task_types(self, tags: str) -> None:
        words = [w for w in tags.split()]
        self.task.config.loss = TaskLoss.NULL
        for item in words:
            if item.startswith(":"):
                self.decode_task_types(item[1:])
        
        location: TaskResource = self.task.resource
        if location.resource_type == ResourceType.VIEW:
            if self.task.config.loss == TaskLoss.NULL:
                self.task.config.loss = TaskLoss.FREE
            if self.task.config.test == TaskTest.NULL:
                self.task.config.test = TaskTest.SELF
        else: # TASK
            if self.task.config.loss == TaskLoss.NULL:
                self.task.config.loss = TaskLoss.PART
            if self.task.config.test == TaskTest.NULL:
                self.task.config.test = TaskTest.TEST

    def __remove_tags_from_title(self, text: str) -> str:
        words: list[str] = [w for w in text.split()]
        output: list[str] = []
        for item in words:
            if item.startswith(":"):
                continue
            if item.startswith("@"):
                continue
            output.append(item)
        return " ".join(output)

    def redirect_from_readme(self, link: str) -> str:
        if not Path(link).is_absolute():
            return str(self.index_path.parent / link)
        return link

    def parse_line(self, line: str, line_num: int = 0) -> Task | None:
        tm = TaskMatcher()
        if not tm.match_full_pattern(line):
            return None
        
        task = self.task
        if tm.key is not None:
            task.basic.key = tm.key
        task.resource.resource_type = ResourceType.VIEW if tm.is_view else ResourceType.EDIT
        task.resource.line_number = line_num
        task.resource.line_data = line
        task.resource.raw_link = tm.task_link
        pre_text = tm.filter_tags(tm.raw_pre + " " + tm.task_title)
        self.__parse_task_types(pre_text)
        task.basic.title = self.__remove_tags_from_title(tm.task_title)

        if task.basic.key == "":
            return None

        # url link tasks
        if tm.task_link.startswith(r"http://") or tm.task_link.startswith(r"https://"):
            if tm.is_view:
                logger.info(t(_TASK_PARSER_VIEW_EXTERNAL_URL, url=tm.task_link))
                self.task.resource.external_url = tm.task_link
                return self.task
            else:
                parser = GithubUrlStructure()
                if parser.parse(tm.task_link):
                    task.resource.remote_git = parser.repository_url
                    task.resource.remote_dir = self.remote_dir
                    task.resource.relative_path = Path(parser.relative_path)
                    task.resource.editable_source = False
                    return task
                else:
                    logger.warning(t(_TASK_PARSER_EDIT_EXTERNAL_URL, url=tm.task_link))
                    task.resource.external_url = tm.task_link
                    task.resource.editable_source = False
                    task.resource.resource_type = ResourceType.VIEW
                    return task
        
        # file view, static task or import task
        path = Path(self.redirect_from_readme(tm.task_link)).resolve()
        task.resource.remote_git = self.remote_url
        task.resource.remote_dir = self.remote_dir
        task.resource.relative_path = path.relative_to(self.remote_dir, walk_up=True)
        task.resource.editable_source = self.editable_source

        return task
    