import typer


def set_sources():
    from .config import set_var_config
    from .utils.vectordb import list_qdrant_db, list_remote_qdrant_db

    set_var_config({"local": list_qdrant_db(), "remote": list_remote_qdrant_db()})


def list_sources():
    from .config import set_var_config
    from .utils.vectordb import list_qdrant_db, list_remote_qdrant_db

    sources = list_qdrant_db()

    if len(sources) != 0:
        typer.secho("Local Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print("* " + "\n* ".join(sources))
    remote_sources = list_remote_qdrant_db()
    print("------------------")
    if len(remote_sources) != 0:
        typer.secho("Remote Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print("* " + "\n* ".join(remote_sources))

    set_var_config({"local": sources, "remote": remote_sources})
