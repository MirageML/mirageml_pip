import typer

def set_sources():
    from .utils.vectordb import list_qdrant_db, list_remote_qdrant_db
    from .config import set_var_config
    set_var_config({
        "local": list_qdrant_db(),
        "remote": list_remote_qdrant_db()
    })

def list_sources():
    from .utils.vectordb import list_qdrant_db, list_remote_qdrant_db
    from .config import set_var_config

    sources = list_qdrant_db()

    if len(sources) != 0:
        typer.secho("Local Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print("* " + "\n* ".join(sources + ["local (this will index the files in your current directory)"]))
    remote_sources = list_remote_qdrant_db()
    print("------------------")
    if len(remote_sources) != 0:
        typer.secho("Remote Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print("* " + "\n* ".join(remote_sources))

    set_var_config({
        "local": sources,
        "remote": remote_sources
    })
