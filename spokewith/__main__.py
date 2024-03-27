import typer

cli = typer.Typer()


@cli.command()
def list():
    """List log entries."""
    print("List")


@cli.command()
def add():
    """Add log entry."""
    print("Log")


@cli.command()
def edit():
    """ "Edit log entry."""
    print("Edit")


@cli.command()
def remove():
    """Delete log entry."""
    print("Delete")


if __name__ == "__main__":
    cli()
