import difflib
from typer.testing import CliRunner
from tko.__main__ import app
import pytest
import os

class Compare:
    @staticmethod
    def load_and_save(filename: str, received: str):
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
    def text(capsys: pytest.CaptureFixture[str], file: str, cmd: str):
        Compare.list(capsys, file, cmd.split(" "))

    # @staticmethod
    # def list(capsys: pytest.CaptureFixture[str], file: str, cmd_list: list[str]):
    #     runner = CliRunner()
    #     result = runner.invoke(app, cmd_list)
    #     expected, received = Compare.load_and_save(file, result.stdout)
    #     assert expected == received


    @staticmethod
    def list(capsys: pytest.CaptureFixture[str], file: str, cmd_list: list[str]):
        runner = CliRunner()
        result = runner.invoke(app, cmd_list)
        expected, received = Compare.load_and_save(file, result.stdout)
        if expected != received:
            diff = "\n".join(difflib.unified_diff(
                expected.splitlines(),
                received.splitlines(),
                fromfile=f"{file}.exp",
                tofile=f"{file}.rec",
                lineterm=""
            ))
            raise AssertionError(
                f"Output mismatch for {file}\n"
                f"command: {' '.join(cmd_list)}\n{diff}"
            )
