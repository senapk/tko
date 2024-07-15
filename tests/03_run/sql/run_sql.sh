#!/bin/bash

tko -m run --cmd "cat create.sql solver.sql | sqlite3" cases.tio
