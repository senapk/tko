#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import run, PIPE
import os
import configparser
import argparse
import tempfile

class Const:
    ansi_green = "\033[92m"
    ansi_reset = "\033[0m"

class Problem:
    tag_value = "value"
    tag_param = "param"
    tag_partial = "partial"


class MyTest:
    def __init__(self, label: str, value: int = 1, partial: bool = True, param: str = "--track"):
        self.label: str = label
        self.awarded: float = 0      # Percentage score (0-100)
        self.value: float = value    # Used to calculate the weighted mean
        self.param: str = param         # Additional parameters for the test
        self.partial: bool = partial # Whether the test can be partially scored

    def set_percentage(self, text: str):
        if text[-1] == "%":
            value = float(text[:-1])
            if self.partial:
                self.awarded = value
            else:
                self.awarded = value if value == 100 else 0
        return self

    
    def run(self):
        temp_file = tempfile.mktemp(prefix="temp_result_file", suffix=".txt")
        extra: list[str] = []
        if self.param:
            extra = self.param.split(" ")
        running_prefix()
        result = run(["tko", "eval", "--timeout", "30", "--none"] + extra + ['-r', temp_file, f"src/{self.label}"], stderr=PIPE, text=True)
        if result.returncode != 0:
           if result.stderr != "":
               print(result.stderr)
        if result.returncode == 0:
            if os.path.isfile(temp_file):
                percent = open(temp_file, "r").read().splitlines()[0].strip()
                self.set_percentage(percent)
                os.remove(temp_file)
        return self


class Grading:
    def __init__(self):
        self.tests: list[MyTest] = []
    def add_and_run_test(self, test: MyTest):
        self.tests.append(test)
        test.run()

    def calc_grade(self) -> int:
        total_weight = sum(test.value for test in self.tests)
        max_label_len = max(len(test.label) for test in self.tests) + 1
        grade: float = 0
        grading_prefix()
        print(f"{'TestCases':<{max_label_len}}| passed | value | earned")
        sep = f"{'-' * max_label_len}|--------|-------|-------"
        grading_prefix()
        print(sep)
        for test in self.tests:
            test.value = test.value * 100 / total_weight
            awarded = test.awarded * test.value / 100
            grading_prefix()
            print(f"{test.label.ljust(max_label_len)}|   {round(test.awarded):3d}% |  {round(test.value):3d}% |   {round(awarded):3d}%")
            grade += awarded
        grading_prefix()
        print(sep)
        grading_prefix()
        print(f"{'Total':<{max_label_len}}|        |  100% |    {Const.ansi_green}{round(grade):3d}%{Const.ansi_reset}")
        return round(grade)

    @staticmethod
    def load_config(config_file: str) -> list[MyTest]:
        config = configparser.ConfigParser()
        config.read(config_file)
        problems: list[MyTest] = []
        for section in config.sections():
            problem = MyTest(
                label=section,
                value=config.getint(section, Problem.tag_value, fallback=1),
                param=config.get(section, Problem.tag_param, fallback=""),
                partial=config.getboolean(section, Problem.tag_partial, fallback=True)
            )
            problems.append(problem)
        return problems
    
    @staticmethod
    def load_readme(readme_file: str) -> list[MyTest]:
        problems: list[MyTest] = []
        if not os.path.isfile(readme_file):
            print(f"README file '{readme_file}' does not exist.")
            return problems
        
        with open(readme_file, "r") as f:
            lines = f.readlines()
        
        for line in lines:
            if not line.startswith("- [ ] `"):
                continue
            test = MyTest("")
            parts = line.split("`")
            title = parts[1].strip()
            words = title.split(" ")
            for w in words:
                if w.startswith("@"):
                    test.label = w[1:]
                elif w.startswith("*"):
                    test.value = int(w[1:])
            if test.label != "":
                problems.append(test)
        return problems

    @staticmethod
    def main(args: argparse.Namespace):
        problems: list[MyTest] = []
        if args.config is not None:
            problems = Grading.load_config(args.config)

        if args.readme is not None:
            problems = Grading.load_readme(args.readme)


        if len(problems) == 0:
            print("No problems found in the configuration file.")
            return

        test_list = Grading()
        for problem in problems:
            test_list.add_and_run_test(problem)

        awarded = test_list.calc_grade()
        if args.output is not None:
            with open(args.output, "w") as f:
                f.write(str(awarded))

def running_prefix():
    print("[TKO RUNNING] ", flush=True, end='')

def grading_prefix():
    print("[TKO GRADING] ", flush=True, end='')

