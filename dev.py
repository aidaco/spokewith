#! /usr/bin/env python
import subprocess
import shutil
from pathlib import Path
from typing import Callable
import functools
import contextlib

from rich.console import Console
import typer

cli = typer.Typer()
HERE = Path()
PKG = HERE / "spokewith"


def sh(*parts: str):
    global console
    result = subprocess.run(parts, capture_output=False)


@cli.command()
def clean(pycache: bool = True, mypycache: bool = True, dist: bool = True):
    global console
    if pycache:
        for match_dir in HERE.glob("**/__pycache__"):
            shutil.rmtree(match_dir, ignore_errors=True)
    if mypycache:
        for match_dir in HERE.glob("**/.mypy_cache"):
            shutil.rmtree(match_dir, ignore_errors=True)
    if dist:
        shutil.rmtree(HERE / "dist", ignore_errors=True)


@cli.command()
def fix(
    fmt: bool = True, isort: bool = True, type_check: bool = True, lint: bool = True
):
    global console
    if fmt:
        sh("python", "-m", "black", str(PKG), "--target-version", "py310")
    if isort:
        sh("python", "-m", "isort", str(PKG))
    if type_check:
        sh("python", "-m", "mypy", str(PKG))
    if lint:
        sh("python", "-m", "flake8", str(PKG))


if __name__ == "__main__":
    console = Console()
    cli()
