from tko.run.run_context import RunContext
from tko.run.filter_mode_service import FilterModeService
from tko.run.wdir import Wdir

class WdirBootstrapService:
    @staticmethod
    def remove_duplicates(ctx: RunContext):
        ctx.target_list = list(dict.fromkeys(ctx.target_list))

    @staticmethod
    def _resolve_lang(ctx: RunContext) -> str | None:
        if ctx.lang:
            return ctx.lang
        if ctx.repo is not None and ctx.repo.data.lang:
            return ctx.repo.data.lang
        return None

    def build(self, ctx: RunContext, filter_mode: FilterModeService):
        ctx.wdir_builded = True
        self.remove_duplicates(ctx)
        if ctx.param.filter:
            ctx.target_list = filter_mode.apply(ctx.target_list)

        try:
            lang = self._resolve_lang(ctx)
            ctx.wdir = Wdir(ctx.settings)
            ctx.wdir.curses_mode = ctx.config.curses_mode
            ctx.wdir.lang = lang
            ctx.wdir.setup_from_target_list(ctx.target_list)
            ctx.wdir.build_unit_list()
            ctx.wdir.filter(ctx.param)
        except FileNotFoundError as err:
            if ctx.wdir.solver:
                executable, _ = ctx.wdir.solver.get_executable()
                executable.set_compile_error(str(err))
        return ctx.wdir