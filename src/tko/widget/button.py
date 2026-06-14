from tko.util.rt import RT
import time

# period in seconds for timed index, default is 0.2s (200ms)
# 0.5 s means 2 updates per second, 0.1s means 10 updates per second
def timed_index(period: float = 0.2) -> int:
    return int(time.time() / period)

class Button:
    @staticmethod
    def sliding_label( info: str, active: bool, active_color: str | None = None, ) -> RT:

        if not active:
            return Button.toggle_bt( info, active=False, enabled=False, )

        info = ":" + info + ":"

        visible = [ i for i, c in enumerate(info) if not c.isspace() ]

        start = timed_index(0.5) % len(visible)
        width = len(visible) // 2

        highlighted: set[int] = {
            visible[(start + offset) % len(visible)]
            for offset in range(width)
        }

        output: list[RT] = []

        for i, char in enumerate(info):

            if i in highlighted:
                output.append( RT( char.upper(), active_color or "G", ) )
            else:
                output.append( RT( char.lower(), active_color or "G", ) )

        return RT.join(output, "")

    @staticmethod
    def toggle_bt(info: str, active: bool, enabled_color: str | None = None, active_color: str | None = None, enabled: bool = True) -> RT:
        sep = " "
        if not enabled: # not enabled
            bg = "X"
            sep = "!"
        elif not active: # enabled but not active
            bg = "C" if active_color is None else active_color
            sep = " "
        else: # enabled and active
            bg = "G" if enabled_color is None else enabled_color
            sep = ":"
        return RT(sep + info + sep, bg)
    
    @staticmethod
    def action_bt(info: str, enabled: bool = True, enabled_color: str | None = None) -> RT:
        return Button.toggle_bt(info, active=False, enabled_color=enabled_color, enabled=enabled)
    
    @staticmethod
    def info_label(info: str, color: str | None = None, sep: str = " ") -> RT:
        return RT(sep + info + sep, color or "Y")