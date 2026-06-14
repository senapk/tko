from typing import Any

from loguru import logger
from pathlib import Path

from tko.util.console import Console
from tko.util.rt import RT


from typing import Any, Protocol

from loguru import logger
from pathlib import Path

from tko.util.console import Console
from tko.util.rt import RT

class ConsoleSink:
    LEVEL_STYLE: dict[str, str] = {
        "DEBUG": "k",
        "INFO": "g",
        "WARNING": "y",
        "ERROR": "r",
        "CRITICAL": "R*",
    }

    def __call__( self, message: Any ) -> None:
        record = message.record

        level = record["level"].name
        # module = record["name"]
        text = record["message"]

        Console.error(
            RT(f"{level:<8}", self.LEVEL_STYLE.get(level, "")),
            text,
            sep=" | ",
        )

def configure_loguru(log_file: Path, debug: bool) -> None:
    logger.remove()
    logger.add(
        ConsoleSink(),
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
