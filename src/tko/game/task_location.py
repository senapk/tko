from __future__ import annotations
from dataclasses import dataclass
from tko.util.git_hub_url import GitHubUrl
from pathlib import Path
from tko.game.task_enums import EvalMode, Materialization

@dataclass(frozen=True, slots=True)
class TaskLocation:
    index_path: Path = Path()
    raw_link: str = ""
    line_number: int = 0
    line_data: str = ""
    eval: EvalMode = EvalMode.NONE
    git_hub_url: GitHubUrl | None = None
    external_source: bool = False
        
    def clone(self) -> TaskLocation:
        return TaskLocation(
            index_path=self.index_path,
            raw_link=self.raw_link,
            line_number=self.line_number,
            line_data=self.line_data,
            eval=self.eval,
            git_hub_url=self.git_hub_url,
            external_source=self.external_source
        )
            
    @property
    def is_non_evaluated(self) -> bool:
        return self.eval == EvalMode.NONE
    
    @property
    def is_http_link(self) -> bool:
        return self.raw_link.startswith("http://") or self.raw_link.startswith("https://")

    @property
    def is_external(self) -> bool:
        """A tarefa precisa de uma cópia de trabalho separada da origem."""
        return self.external_source or self.is_task_from_git

    @property
    def materialization(self) -> Materialization:
        return Materialization.EXTERNAL if self.is_external else Materialization.LOCAL
        
    @property
    def is_task_from_git(self) -> bool:
        return self.git_hub_url is not None
