class Log:
    _verbose = False
    
    @staticmethod
    def set_verbose(verbose: bool):
        Log._verbose = verbose

    @staticmethod
    def verbose(*args, **kwargs):
        if Log._verbose:
            print(*args, **kwargs)

    @staticmethod
    def resume(*args, **kwargs):
        if not Log._verbose:
            print(*args, **kwargs)
            print("", end="", flush=True)
