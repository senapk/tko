#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Optional, List
import re
import os
import argparse
from tko.util.decoder import Decoder


def get_label(line) -> Optional[str]:
    if "@" not in line:
        return None
    label = line.split('@')[1].split(' ')[0].split(']')[0]
    return label

def get_hook_from_line(line, base) -> Optional[str]:
    base = clear_base(base)
    if "/Readme.md)" in line and base in line and not "https:" in line:
        try:
            hook = line.split(base + '/')[1].split('/')[0]
            return hook
        except:
            print("fail: error in", line)
            exit(1)
            pass
    return None

def load_title_from_file(path) -> str:
    data = Decoder.load(path)
    header = data.splitlines()[0]
    if (len(header) == 0):
        print('fail: Empty header in ', path)
        exit(1)
    if not header.startswith('# '):
        print('fail: first line should start with # in ', path)
        exit(1)
    words = header.split(' ')
    if len(words) < 2:
        print('fail: header must have any word ', path)
        exit(1)
    return " ".join(words[1:])

def loading_titles_from_files(path):
    content = Decoder.load(path)
    lines = content.splitlines()

    output = []

    for line in lines:
        match = re.search(r'\[([^\[]*?)\]\((.*?)\)', line)
        data = line
        if match:
            link = match.group(2)
            if link.endswith('md') and not link.startswith('http'):
                if not os.path.isfile(link):
                    print("fail:", link, ' not found')
                else:
                    title = load_title_from_file(match.group(2))
                    data = line.replace(match.group(1), title)
        output.append(data)

    Decoder.save(path, '\n'.join(output))

def clear_base(base):
    if base[-1] == '/':
        base = base[:-1]
    if base[0] == '/':
        base = base[1:]
    if base[0] == '.':
        base = base[1:]
    return base

def found_labels_mismatch(path, base) -> bool:
    error_found = False
    base = clear_base(base)
    print("Checking mismatch in labels")
    data = Decoder.load(path)
    lines = data.splitlines()

    not_ok = []
    count_ok = 0
    for line in lines:
        hook = get_hook_from_line(line, base)
        if hook is None:
            continue
        label = get_label(line)
        if label is None:
            print("fail: error in", line)
            error_found = True
            continue
        if label == hook:
            count_ok += 1
        else:
            not_ok.append("    ({} != {}): {}".format(label, hook, os.path.join(base, hook, 'Readme.md')))
            error_found = True

    print("- verified:", count_ok)
    print("- mismatch:", len(not_ok))
    for line in not_ok:
        print(line)
    return error_found

# check for all folders in the base folder searching for missing labels
def found_unused_hooks(path, base_dir) -> bool:
    print("Checking for unused hooks")
    data = Decoder.load(path)
    lines = data.splitlines()
    hooks_all = [get_hook_from_line(line, base_dir) for line in lines]
    # create a set of hooks
    hooks = set(hooks_all)

    # create a list with folders in base dir if base/folder/Readme.md exists
    folders = []
    for folder in os.listdir(base_dir):
        if os.path.isfile(base_dir + '/' + folder + '/Readme.md'):
            folders.append(folder)

    missing = [f for f in folders if f not in hooks]

    if len(missing) > 0:
        print("Missing entries:")
        for m in missing:
            title = load_title_from_file(os.path.join(base_dir, m, 'Readme.md'))
            path = os.path.join(base_dir, m, 'Readme.md')
            print("- [{}]({})".format(title, path))
        return True
    return False


def indexer_main(args):
    loading_titles_from_files(args.path)
    if found_labels_mismatch(args.path, args.base):
        exit(1)
    if found_unused_hooks(args.path, args.base):
        exit(1)
