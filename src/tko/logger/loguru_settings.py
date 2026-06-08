from loguru import logger
import sys
from pathlib import Path

def configure_loguru(log_file: Path) -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="WARNING",
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
    
