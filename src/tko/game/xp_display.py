from math import trunc


def format_task_xp(value: float) -> str:
    """Format task XP in at most three cells for the tree prefix."""
    if value < 10:
        return f"{trunc(value * 10) / 10:.1f}"
    return str(trunc(value))


def truncate_total_xp(value: float) -> int:
    """Hide fractional XP from aggregate displays without changing calculations."""
    return trunc(value)
