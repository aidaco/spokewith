from pathlib import Path

import typer
from rich import print
from rich.align import Align
from rich.console import Console, Group
from rich.table import Table

cli = typer.Typer()


@cli.command()
def show():
    """Show logged calls."""
    print("Show")


@cli.command()
def log():
    """Log call(s)."""
    print("Log")


@cli.command()
def edit():
    """ "Edit log entry."""
    print("Edit")


@cli.command()
def delete():
    """Delete log entry."""
    print("Delete")


if __name__ == "__main__":
    cli()
