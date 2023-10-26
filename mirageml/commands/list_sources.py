import typer


def get_sources():
    from .utils.vectordb import list_local_qdrant_db, list_remote_qdrant_db

    return list_local_qdrant_db(), list_remote_qdrant_db()


def set_sources():
    from .config import set_var_config
    from .utils.vectordb import list_local_qdrant_db, list_remote_qdrant_db
    remote_sources = list_remote_qdrant_db()

    set_var_config({"local": list_local_qdrant_db(), "remote": remote_sources})


def list_sources():
    import sys

    from .config import set_var_config
    from .utils.vectordb import list_local_qdrant_db, list_remote_qdrant_db

    sources = list_local_qdrant_db()
    remote_sources = list_remote_qdrant_db()

    if len(sources) == 0 and len(remote_sources) == 0:
        typer.secho(
            f"No sources found. Please add a source using {sys.argv[0].split('/')[-1]} add source",
            fg=typer.colors.RED,
            bold=True,
        )
        return

    if len(sources) != 0:
        typer.secho("Local Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print("* " + "\n* ".join(sources))

    if len(remote_sources) != 0:
        if len(sources) != 0:
            print("------------------")
        typer.secho("Remote Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print("* " + "\n* ".join(remote_sources))

    set_var_config({"local": sources, "remote": remote_sources})
