#!/usr/bin/env python3
"""Convenience wrapper: python3 run_systolic.py"""
import sys, subprocess
script = "examples/systolic_array/run_systolic.py"
sys.exit(subprocess.call([sys.executable, script] + sys.argv[1:]))
