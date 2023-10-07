#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date
import os

today = date.today()

file = ".bin/last_update.txt"

if not os.path.isfile(file): # create empty file if not exists
    with open(file, "w") as f:
        f.write("")
            
with open(file) as f:
    last_update = f.read()

if last_update != today.strftime("%Y-%m-%d"):
    with open(file, "w") as f:
        f.write(today.strftime("%Y-%m-%d"))
    print("Checking for updates")
    os.system("bash update.sh > /dev/null 2>&1")
