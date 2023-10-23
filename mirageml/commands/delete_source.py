from .utils.vectordb import delete_qdrant_db, delete_remote_qdrant_db


def delete_source(names: list[str]):
    import typer

    from .config import load_config

    config = load_config()
    sources = config["local"] + config["remote"]

    for name in names:
        while True:
            if name not in sources:
                typer.secho(
                    f"Source: {name} does not exist. Choose one of the following or exit:",
                    fg=typer.colors.BRIGHT_RED,
                )
                print("\n".join(sources))
                name = typer.prompt("Enter source name", default="exit", show_default=False)
                if not name or name == "exit":
                    return
            else:
                break

        typer.secho(f"Deleting Source: {name}...", fg=typer.colors.BRIGHT_RED)
        delete_qdrant_db(name)
        delete_remote_qdrant_db(name)
        print(f"Deleted Source: {name}")
