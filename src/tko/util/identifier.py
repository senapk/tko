from tko.enums.identifier_type import IdentifierType

import os

class Identifier:
    def __init__(self):
        pass

    @staticmethod
    def get_type(target: str) -> IdentifierType:
        if os.path.isdir(target):
            return IdentifierType.OBI
        elif target.endswith(".md"):
            return IdentifierType.MD
        elif target.endswith(".tio"):
            return IdentifierType.TIO
        elif target.endswith(".vpl") or target.endswith(".cases"):
            return IdentifierType.VPL
        else:
            return IdentifierType.SOLVER