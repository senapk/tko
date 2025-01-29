from tko.__main__ import Parser, exec
import os

class Compare:
    @staticmethod
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
    
    @staticmethod
    def text(capsys, file: str, cmd: str):
        Compare.list(capsys, file, cmd.split(" "))

    @staticmethod
    def list(capsys, file: str, cmd_list: list[str]):
        parser = Parser().parser
        args = parser.parse_args(cmd_list)
        exec(parser, args)
        expected, received = Compare.load_and_save(file, capsys.readouterr().out)
        assert expected == received
