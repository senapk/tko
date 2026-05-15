class RunConfig:
    """Immutable configuration set before execution (flags, timeout, modes)."""

    def __init__(self):
        self.curses_mode: bool = False
        self.run_without_ask: bool = True
        self.show_track_info: bool = False
        self.show_self_info: bool = False
        self.eval_mode: bool = False
        self.complex_percent: bool = False
        self.abord_on_exec_error: bool = False
        self.no_run: bool = False
        self.timeout: int = 0
