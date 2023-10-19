import typer
from .utils.vectordb import list_qdrant_db, list_remote_qdrant_db

def list_sources():
    sources = list_qdrant_db()
    if len(sources) == 0:
        typer.secho("No local sources. Create a source with `mirageml add source`", fg=typer.colors.BRIGHT_RED, bold=True)
    else:
        typer.secho("Local Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        for source in sources:
            print(source)
    remote_sources = list_remote_qdrant_db()
    if len(remote_sources) == 0:
        typer.secho("No remote sources. Create a source with `mirageml add source`", fg=typer.colors.BRIGHT_RED, bold=True)
    else:
        typer.secho("Remote Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        for source in remote_sources:
            print(source)

