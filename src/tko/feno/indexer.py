#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import argparse
from tko.util.decoder import Decoder

class TaskLine:
    def __init__(self, line: str = ""):
        self.line: str = line
        self.isTask: bool = False
        self.pre: str = ""
        self.title: str = ""
        self.link: str = ""
        self.pos: str = ""
    
    def init_by_line(self):
        regex = r'- \[ \](.*)\[(.+)\]\((.+)\)(.*)'
        match = re.search(regex, self.line)
        if match:
            self.isTask = True
            self.pre = match.group(1)
            self.title = match.group(2)
            self.link = match.group(3)
            self.pos = match.group(4)
        return None

    def init_by_hook(self, hook: str):
        self.isTask = True
        self.link = os.path.join("base", hook, "Readme.md")
        self.pre = f" `@{hook}` "
        self.load_title_from_link()

    def get_label(self) -> None | str:
        line = self.pre + " " + self.title + " " + self.pos
        if "@" not in line:
            return None
        label = line.split('@')[1]
        valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
        valid_label = ""
        for char in label:
            if char in valid_chars:
                valid_label += char
            else:
                break
        if len(valid_label) == 0:
            print("fail: error in", line)
            return None
        return valid_label

    def get_hook(self) -> None | str:
        if self.link.endswith("/Readme.md") and self.link.startswith("base/"):
            try:
                hook = self.link.split("/")[-2]
                return hook
            except Exception as e:
                print("fail: error in", self.link, "with exception:", e)
                exit(1)
        return None

    def load_title_from_link(self) -> str:
        link = self.link
        data = Decoder.load(link)
        header = data.splitlines()[0]
        if len(header) == 0:
            print('fail: Empty header in ', link)
            exit(1)
        if not header.startswith('# '):
            print('fail: first line should start with # in ', link)
            exit(1)
        words = header.split(' ')
        if len(words) < 2:
            print('fail: header must have any word ', link)
            exit(1)
        return " ".join(words[1:])
    
    def make_new_line(self) -> str:
        if self.isTask:
            label = self.get_label()
            hook = self.get_hook()
            if hook is not None:
                pre = self.pre
                pos = self.pos
                if label is not None:
                    if label != hook and not label.startswith(hook + "_"):
                        print(f"Warning: label:{label}, hook:{hook}")
                    # pre = self.pre.replace("@" + label, "@" + hook)
                    # pos = self.pos.replace("@" + label, "@" + hook)
                title = self.load_title_from_link()
                return f"- [ ]{pre}[{title}]({self.link}){pos}"
        return self.line

def loading_titles_from_files(path: str) -> list[TaskLine]:
    content = Decoder.load(path)
    lines = content.splitlines()

    output: list[str] = []
    task_lines = [TaskLine(line) for line in lines]
    for taskLine in task_lines:
        taskLine.init_by_line()
        line = taskLine.line
        if taskLine.isTask:
            line = taskLine.make_new_line()
        output.append(line)

    Decoder.save(path, '\n'.join(output))
    return task_lines


# def found_labels_mismatch(path: str, base: str) -> bool:
#     error_found = False
#     base = clear_base(base)
#     print("Checking mismatch in labels")
#     data = Decoder.load(path)
#     lines = data.splitlines()

#     not_ok: list[str] = []
#     count_ok = 0
#     for line in lines:
#         hook = get_hook_from_line(line, base)
#         if hook is None:
#             continue
#         label = get_label(line)
#         if label is None:
#             print("fail: error in", line)
#             error_found = True
#             continue
#         if label == hook:
#             count_ok += 1
#         else:
#             not_ok.append("    ({} != {}): {}".format(label, hook, os.path.join(base, hook, 'Readme.md')))
#             error_found = True

#     print("- verified:", count_ok)
#     print("- mismatch:", len(not_ok))
#     for line in not_ok:
#         print(line)
#     return error_found

# check for all folders in the base folder searching for missing labels
def found_unused_hooks(task_lines: list[TaskLine], base_dir: str) -> bool:
    print("Checking for unused hooks")
    hooks_all: list[str] = []
    for tline in task_lines:
        if tline.isTask:
            hook = tline.get_hook()
            if hook is not None:
                hooks_all.append(hook)
    # create a set of hooks
    hooks = set(hooks_all)

    # create a list with folders in base dir if base/folder/Readme.md exists
    folders: list[str] = []
    for folder in os.listdir(base_dir):
        if os.path.isfile(base_dir + '/' + folder + '/Readme.md'):
            folders.append(folder)

    missing = [f for f in folders if f not in hooks]

    if len(missing) > 0:
        print("Missing entries:")
        print(missing)
        for m in missing:
            task_line = TaskLine()
            task_line.init_by_hook(m)
            print(task_line.make_new_line())
        return True
    return False


def indexer_main(args: argparse.Namespace):
    task_lines: list[TaskLine] = loading_titles_from_files(args.path)
    # if found_labels_mismatch(args.path, args.base):
    #     exit(1)
    if found_unused_hooks(task_lines, args.base):
        exit(1)
