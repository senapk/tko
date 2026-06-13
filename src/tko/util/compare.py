import difflib
from collections.abc import Sequence
from typer.testing import CliRunner
from tko.__main__ import app
from tko.util.console import Console
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

    @staticmethod
    def run(cmd_list: Sequence[str] | str) -> str:
        runner = CliRunner()
        if isinstance(cmd_list, str):
            cmd_list = cmd_list.split(" ")
        full_cmd = cmd_list if "--lang" in cmd_list else ["--lang", "pt", *cmd_list]
        with Console.capture() as captured:
            result = runner.invoke(app, full_cmd)
        if result.exception:
            raise result.exception
        return result.stdout + captured.getvalue()

    # @staticmethod
    # def list(capsys: pytest.CaptureFixture[str], file: str, cmd_list: list[str]):
    #     runner = CliRunner()
    #     result = runner.invoke(app, cmd_list)
    #     expected, received = Compare.load_and_save(file, result.stdout)
    #     assert expected == received


    @staticmethod
    def list(capsys: pytest.CaptureFixture[str], file: str, cmd_list: Sequence[str]):
        full_cmd = cmd_list if "--lang" in cmd_list else ["--lang", "pt", *cmd_list]
        received = Compare.run(full_cmd)
        expected, received = Compare.load_and_save(file, received)
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
                f"command: {' '.join(full_cmd)}\n{diff}"
            )
