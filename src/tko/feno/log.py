from typing import Any
from tko.util.console import Console

class Log:
    _verbose = False
    
    @staticmethod
    def set_verbose(verbose: bool):
        Log._verbose = verbose

    @staticmethod
    def verbose(*args: str, **kwargs: Any):
        if Log._verbose:
            Console.print(*args, **kwargs)

    @staticmethod
    def resume(*args: str, **kwargs: Any):
        if not Log._verbose:
            Console.print(*args, **kwargs)
            Console.print("", end="", flush=True)
