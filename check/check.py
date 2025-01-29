#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date
import os

today = date.today()
rep_name = os.environ["REPL_SLUG"]
# last_update.txt send from bashrc
file = "/home/runner/" + rep_name + "/.bin/last_update.txt"

today_str = today.strftime("%Y-%m-%d")

if not os.path.isfile(file): # create empty file if not exists
    with open(file, "w") as f:
        f.write(today_str)
            
with open(file) as f:
    last_update = f.read()

if last_update != today_str:
    with open(file, "w") as f:
        f.write(today_str)
    print("Checking for updates")
    os.system(f"/home/runner/{rep_name}/.bin/update.sh")
