import os
from typing import List
from tko.__main__ import exec, Parser

def load_and_save(filename, received):
    folder = "compare"
    if not os.path.isdir(folder):
        os.mkdir(folder)
    rec = os.path.join(folder, filename + ".rec")
    exp = os.path.join(folder, filename + ".exp")
    open(rec, "w").write(received)
    if os.path.isfile(exp):
        expected = open(exp).read()
    else:
        open(exp, "w").write(received)
        expected = received
    return expected, received

def compare_text(capsys, move_dir: str, file: str, cmd: str):
    compare_list(capsys, move_dir, file, cmd.split(" "))

def compare_list(capsys, move_dir: str, file: str, cmd_list: List[str]):
    old_folder = os.getcwd()
    os.chdir(move_dir)
    parser = Parser().parser
    args = parser.parse_args(cmd_list)
    exec(parser, args)
    expected, received = load_and_save(file, capsys.readouterr().out)
    os.chdir(old_folder)
    assert expected == received