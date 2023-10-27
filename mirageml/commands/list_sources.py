import sys

import typer


def get_sources():
    from .utils.vectordb import list_local_qdrant_db, list_remote_qdrant_db

    return list_local_qdrant_db(), list_remote_qdrant_db()


def set_sources(local_sources=None, remote_sources=None):
    from .config import set_var_config
    from .utils.vectordb import list_local_qdrant_db, list_remote_qdrant_db

    if not local_sources:
        local_sources = list_local_qdrant_db()
    if not remote_sources:
        remote_sources = list_remote_qdrant_db()

    set_var_config({"local": local_sources, "remote": remote_sources})


def list_sources():
    local_sources, remote_sources = get_sources()

    if len(local_sources) == 0 and len(remote_sources) == 0:
        typer.secho(
            f"No sources found. Please add a source using {sys.argv[0].split('/')[-1]} add source",
            fg=typer.colors.RED,
            bold=True,
        )
        return

    if len(local_sources) != 0:
        typer.secho("Local Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print("* " + "\n* ".join(local_sources))

    if len(remote_sources) != 0:
        if len(local_sources) != 0:
            print("------------------")
        typer.secho("Remote Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print("* " + "\n* ".join(remote_sources))

    set_sources(local_sources, remote_sources)
