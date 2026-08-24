# Configuration has moved to pyproject.toml. This shim exists only so that
# `pip install -e .` keeps working on older pip/setuptools. All metadata,
# dependencies, packages, and the console entry point are declared in
# pyproject.toml.
from setuptools import setup

setup()
