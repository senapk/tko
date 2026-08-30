from __future__ import annotations

from dataclasses import dataclass

from tko.run.run_config import RunConfig


@dataclass(frozen=True)
class RunExecutionSettings:
    no_run: bool = False
    timeout: int = 0
    curses_mode: bool = False
    show_track_info: bool = False
    show_self_info: bool = False
    run_without_ask: bool = True
    eval_mode: bool = False
    complex_percent: bool = False
    abord_on_exec_error: bool = False

    @classmethod
    def from_config(cls, config: RunConfig) -> "RunExecutionSettings":
        return cls(
            no_run=config.no_run,
            timeout=config.timeout,
            curses_mode=config.curses_mode,
            show_track_info=config.show_track_info,
            show_self_info=config.show_self_info,
            run_without_ask=config.run_without_ask,
            eval_mode=config.eval_mode,
            complex_percent=config.complex_percent,
            abord_on_exec_error=config.abord_on_exec_error,
        )
