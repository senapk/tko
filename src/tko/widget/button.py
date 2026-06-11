from tko.util.rt import RT

class Button:
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
    def info_label(info: str, color: str | None = None) -> RT:
        return RT(" " + info + " ", color or "Y")