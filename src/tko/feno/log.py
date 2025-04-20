from typing import Any

class Log:
    _verbose = False
    
    @staticmethod
    def set_verbose(verbose: bool):
        Log._verbose = verbose

    @staticmethod
    def verbose(*args: str, **kwargs: Any):
        if Log._verbose:
            print(*args, **kwargs)

    @staticmethod
    def resume(*args: str, **kwargs: Any):
        if not Log._verbose:
            print(*args, **kwargs)
            print("", end="", flush=True)
