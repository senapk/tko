import sys
from loguru import logger
from pathlib import Path

def configure_loguru(log_file: Path, debug: bool) -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG" if debug else "INFO",
        format="<level>{level: <8}</level> | <level>{message}</level>",
    )
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            level="DEBUG",
            rotation="50 MB",
            retention="14 days",
            compression="gz",
        )
    except OSError:
        pass
    
    logger.level("INFO", color="<green>")
