import typer
from .utils.vectordb import list_qdrant_db, list_remote_qdrant_db

def list_sources():
    sources = list_qdrant_db()
    sources.append("local (this will index the files in your current directory)")
    if len(sources) != 0:
        typer.secho("Local Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print("\n* ".join(sources))
    remote_sources = list_remote_qdrant_db()
    print("------------------")
    if len(remote_sources) != 0:
        typer.secho("Remote Sources:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        print("\n* ".join(remote_sources))

def help_list_sources():
    sources = list_qdrant_db()
    remote_sources = list_remote_qdrant_db()
    all_sources = list(set(sources + remote_sources))
    if len(all_sources) == 0:
        final_string = "Specify sources to use as context:\n\n\n**mml chat -s {source1} -s {source2}**\n\n\n\n"
    elif len(all_sources) == 1:
        final_string = f"Specify sources to use as context:\n\n\nEx: **mml chat -s {all_sources[0]}**\n\n\n\n"
    else:
        final_string = f"Specify sources to use as context:\n\n\nEx: **mml chat -s {all_sources[0]} -s {all_sources[1]}**\n\n\n\n"

    sources.append("local (this will index the files in your current directory)")
    if len(sources) != 0:
        final_string += "**Local Sources:**\n\n* "
        final_string +="\n\n* ".join(sources)
    final_string +="\n\n---\n\n"
    if len(remote_sources) != 0:
        final_string += "**Remote Sources:**\n\n* "
        final_string +="\n\n* ".join(remote_sources)
    return final_string