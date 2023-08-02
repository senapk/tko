# Console scripts

import argparse

from .__init__ import __version__  # all imports require a dot when building package: '.__init__', etc.
from .utils.general import colorstr
from .simple import add_one

prefix = colorstr('ultralytics: ')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('number', nargs='?', type=int, default=1, help='number')

    opt = parser.parse_args()
    print(f'{prefix}add_one({opt.number}) = {add_one(opt.number)}')

if __name__ == '__main__':
    main()
