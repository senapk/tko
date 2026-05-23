from pathlib import Path

from tko.play.opener import Opener
from tko.run.run_context import RunContext


class OpenerFactory:
    @staticmethod
    def create_for_wdir(ctx: RunContext) -> Opener:
        opener = Opener(ctx.settings)
        folders: list[Path] = []
        targets: list[Path] = [Path(".")]
        if ctx.target_list:
            targets = ctx.target_list

        solver = ctx.wdir.solver
        if solver is None:
            return opener
        if ctx.wdir.lang is not None:
            opener.set_language(ctx.wdir.lang)
        elif solver.args_list:
            solver_zero = solver.args_list[0]
            lang = solver_zero.name.split(".")[-1]
            opener.set_language(lang)

        for target in targets:
            if target.is_dir() and target not in folders:
                opener.add_task_folder_to_open(target)
            else:
                opener.add_files_to_open([target])
        return opener