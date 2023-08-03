#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import math

import sys
from enum import Enum
from typing import List, Tuple, Any, Optional
import os
import re
import shutil
import argparse
import subprocess
import tempfile
import io
import urllib.request
import urllib.error
import json
from subprocess import PIPE
import configparser
from appdirs import user_data_dir

from .colored import Colored, Color
from .symbol import Symbol
from .unit import Unit
from .solver import Solver
from .vpl_parser import VplParser
from .loader import Loader
from .enums import ExecutionResult, DiffMode, IdentifierType, Identifier
from .param import Param
from .wdir import Wdir
from .label_factory import LabelFactory
from .runner import Runner
from .execution import Execution
from .report import Report
from .diff import Diff
from .pattern_loader import PatternLoader
from .writer import Writer
from .replacer import Replacer
from .actions import Actions





