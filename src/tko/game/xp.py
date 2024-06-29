from typing import Optional
import re

class XP:
    token_level_one = "level_one"
    token_level_mult = "level_mult"
    level_one: int = 100
    level_mult: float = 1.5
    
    @staticmethod
    def get_level(xp: int) -> int:
        level = 1
        while XP.get_xp(level) <= xp:
            level += 1
        return level - 1
    
    @staticmethod
    def get_xp(level: int) -> int:
        total = 0
        for i in range(level - 1):
            total += XP.level_one * (XP.level_mult ** i)
        return int(total)

    @staticmethod
    def load_html_tags(task: str) -> Optional[str]:
        pattern = r"<!--\s*(.*?)\s*-->"
        match = re.search(pattern, task)
        if not match:
            return None
        return match.group(1).strip()

    @staticmethod
    def parse_settings(line: str):
        values = XP.load_html_tags(line)
        if values is not None:
            tags = values.split(" ")
            for t in tags:
                if t.startswith(XP.token_level_one):
                    XP.level_one = int(t.split(":")[1])
                if t.startswith(XP.token_level_mult):
                    XP.level_mult = float(t.split(":")[1])
