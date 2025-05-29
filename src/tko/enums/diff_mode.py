# from typing import override


import enum


class DiffMode(enum.Enum): # não mude os valores pois são utilizados no json
    SIDE = "side"
    DOWN = "down"