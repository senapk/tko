#!/bin/python3

import os
import argparse

# function that navigates through the directory recursively and return
# all files that begins with test_ and ends with .sh
def get_test_files(directory):
    test_files = []

    # get all files in the current directory
    entries = os.listdir(directory)
    entries = [os.path.join(directory, entry) for entry in entries]
    entries = [os.path.normpath(os.path.abspath(entry)) for entry in entries]

    files = [entry for entry in entries if os.path.isfile(entry)]
    folders = [entry for entry in entries if os.path.isdir(entry)]
    

    # filter the files that begins with test_ and ends with .sh
    for f in files:
        if f.endswith(".sh"):
            test_files.append(f)

    for f in folders:
        test_files += get_test_files(f)

    return test_files


argparser = argparse.ArgumentParser()
argparser.add_argument("-r", "--run", action="store_true", help="run all tests")
argparser.add_argument("-c", "--clean", action="store_true", help="clean all tests")

args = argparser.parse_args()

scripts = get_test_files(".")

if not args.run and not args.clean:
    args.run = True

root = os.getcwd()
cut = len(root) + 1

scripts = sorted(scripts)
for script in scripts:
    dirname = os.path.dirname(script)
    filename = os.path.basename(script)
    outfile = os.path.join(dirname, "zz_" + filename[:-2] + "out")
    userfile = os.path.join(dirname, "zz_" + filename[:-2] + "user")

    if args.run:
        os.chdir(dirname)
        cmd = "bash " + filename + " &> " + outfile
        os.system(cmd)

