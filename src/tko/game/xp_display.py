from math import trunc


def format_task_xp(value: float) -> str:
    """Format an individual task XP value with one truncated decimal place."""
    return f"{trunc(value * 10) / 10:.1f}"


def truncate_total_xp(value: float) -> int:
    """Hide fractional XP from aggregate displays without changing calculations."""
    return trunc(value)
