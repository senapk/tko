#!/bin/bash

tko -m run
echo ""

tko -m run cases.t
echo ""

tko -m run solver.py cases.t
echo ""

tko -m run solver.p cases.tio
echo ""

