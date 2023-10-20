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
    final_string = "Please specify sources to use for RAG using mml rag --sources <sources>\n\n\n\n"
    if len(sources) != 0:
        final_string += "**Local Sources:**\n\n* "
        final_string +="\n\n* ".join(sources)
    remote_sources = list_remote_qdrant_db()
    final_string +="\n\n---\n\n"
    if len(remote_sources) != 0:
        final_string += "**Remote Sources:**\n\n* "
        final_string +="\n\n* ".join(remote_sources)
    return final_string