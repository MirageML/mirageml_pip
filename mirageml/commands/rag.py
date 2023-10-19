import re
import typer
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt

from .config import load_config
from .add_source import add_local_source
from .utils.brain import llm_call
from .utils.vectordb import list_qdrant_db, list_remote_qdrant_db, qdrant_search, remote_qdrant_search
from .utils.prompt_templates import RAG_TEMPLATE

console = Console()
config = load_config()

def get_remote_sources():
    # Get a list of available data sources and include the local directory as an option
    possible_sources = list_remote_qdrant_db()

    if not possible_sources: return []

    # User selection of sources to use
    while True:
        typer.secho("Here are the possible remote sources you can use:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        for source in possible_sources:
            typer.secho(f" - {source}", fg=typer.colors.GREEN, bold=True)

        sources_input = Prompt.ask("Which sources would you like to use? (separate multiple sources with a space or comma)", default="", show_default=False)
        sources = [source.strip() for source in re.split(',|\s+', sources_input) if source.strip()]

        invalid_sources = [source for source in sources if source not in possible_sources]
        if invalid_sources:
            for source in invalid_sources:
                typer.secho(f"Invalid source: {source}", fg=typer.colors.BRIGHT_RED, bold=True)
            continue
        else: break

    return sources

def get_local_sources():
    # Get a list of available data sources and include the local directory as an option
    possible_sources = list_qdrant_db() + ["local"]

    # User selection of sources to use
    while True:
        typer.secho("Here are the possible local sources you can use:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        for source in possible_sources:
            if source == "local":
                typer.secho(f" - {source} (this will index the files in your local directory)", fg=typer.colors.GREEN, bold=True)
            else:
                typer.secho(f" - {source}", fg=typer.colors.GREEN, bold=True)

        sources_input = Prompt.ask("Which sources would you like to use? (separate multiple sources with a space or comma)", default="local", show_default=True)
        sources = [source.strip() for source in re.split(',|\s+', sources_input) if source.strip()]

        invalid_sources = [source for source in sources if source not in possible_sources]
        if invalid_sources:
            for source in invalid_sources:
                typer.secho(f"Invalid source: {source}", fg=typer.colors.BRIGHT_RED, bold=True)
            continue
        else:
            break

    # Check if user doesn't specify any source
    if not sources:
        typer.secho("By default Mirage will index the files under the current directory.", fg=typer.colors.RED, bold=True)
        typer.secho("If you want to run RAG over other sources, please specify them with `--sources`.", fg=typer.colors.BRIGHT_RED, bold=True)
        user_input = Prompt.ask("If you'd like to proceed type 'yes'", default="yes", show_default=True)
        if user_input.lower().startswith("y"):
            sources = ["local"]
        else: return []

    # Handle local source
    if "local" in sources:
        sources.remove("local")
        sources.append(add_local_source())

    return sources

def search(live, user_input, local_sources, remote_sources=None):
    hits = []
    for source_name in local_sources:
        live.update(Panel("Searching through local sources...", title="[bold blue]Assistant[/bold blue]", border_style="blue"))
        try:
            # Search for matches in each source based on user input
            hits.extend(qdrant_search(source_name, user_input))
        except:
            # Handle potential errors with mismatched embedding models
            error_msg_local = f"Source: {source_name} was created with OpenAI's embedding model. Please run with `local_mode=False` or reindex with `mirageml delete source {source_name}; mirageml add source {source_name}`."
            error_msg_openai = f"Source: {source_name} was created with a local embedding model. Please run with `local_mode=True` or reindex with `mirageml delete source {source_name}; mirageml add source {source_name}`."

            typer.secho(error_msg_local if config["local_mode"] else error_msg_openai, fg=typer.colors.RED, bold=True)
            return

    for source_name in remote_sources:
        live.update(Panel("Searching through remote sources...", title="[bold blue]Assistant[/bold blue]", border_style="blue"))
        hits.extend(remote_qdrant_search(source_name, user_input))

    return hits

def rank_hits(hits):
    # Rank the hits based on their relevance
    sorted_hits = sorted(hits, key=lambda x: x["score"], reverse=True)[:5]
    return sorted_hits

def create_context(sorted_hits):
    return "\n\n".join([str(x["payload"]["source"]) + ": " + x["payload"]["data"] for x in sorted_hits])

def search_and_rank(live, user_input, local_sources, remote_sources=None):
    hits = search(live, user_input, local_sources, remote_sources)
    sorted_hits = rank_hits(hits)
    return sorted_hits

def rag_chat():
    # Load configuration settings
    local_sources = get_local_sources()
    remote_sources = get_remote_sources()

    sources = remote_sources + local_sources

    # Beginning of the chat sequence
    user_input = Prompt.ask(f"Chat with Mirage ({', '.join(sources)})", default="exit", show_default=False)

    # Live display while searching for relevant sources
    with Live(Panel("Searching for the relevant sources...",
                title="[bold blue]Assistant[/bold blue]", border_style="blue"),
                console=console, screen=True, auto_refresh=True, vertical_overflow="visible") as live:

        sorted_hits = search_and_rank(live, user_input, local_sources, remote_sources)
        context = create_context(sorted_hits)

        # Chat history that will be sent to the AI model
        chat_history = [
            {"role": "system", "content": "You are a helpful assistant that responds to questions concisely with the given context in the following format:\n{answer}\n\nSources:\n{sources}"},
            {"role": "user", "content": RAG_TEMPLATE.format(context=context, question=user_input, sources=sources)}
        ]

        # Fetch the AI's response
        ai_response = ""
        live.update(Panel("Found relevant sources! Answering question...", title="[bold blue]Assistant[/bold blue]", border_style="blue"))
        response = llm_call(chat_history, model=config["model"], stream=True, local=config["local_mode"])

        if config["local_mode"]:
            for chunk in response:
                ai_response += chunk
                live.update(Panel(Markdown(ai_response), title="[bold blue]Assistant[/bold blue]", border_style="blue"))
        else:
            for chunk in response.iter_content(1024):
                if chunk:
                    decoded_chunk = chunk.decode('utf-8')
                    ai_response += decoded_chunk
                    live.update(Panel(Markdown(ai_response), title="[bold blue]Assistant[/bold blue]", border_style="blue"))

    # Print the AI's response
    console.print(Panel(Markdown(ai_response), title="[bold blue]Assistant[/bold blue]", border_style="blue"))

    # Loop for follow-up questions
    while True:
        try:
            user_input = Prompt.ask("Ask a follow-up", default="exit", show_default=False)
            if user_input.lower() == 'exit':
                typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
                break
        except KeyboardInterrupt:
            typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
            break

        chat_history.append({"role": "user", "content": user_input})

        with Live(Panel("Assistant is typing...", title="[bold blue]Assistant[/bold blue]", border_style="blue"),
                console=console, screen=True, auto_refresh=True, vertical_overflow="visible") as live:

            response = llm_call(chat_history, model=config["model"], stream=True, local=config["local_mode"])

            ai_response = ""
            if config["local_mode"]:
                for chunk in response:
                    ai_response += chunk
                    live.update(Panel(Markdown(ai_response), title="[bold blue]Assistant[/bold blue]", border_style="blue"))
            else:
                for chunk in response.iter_content(1024):
                    if chunk:
                        decoded_chunk = chunk.decode('utf-8')
                        ai_response += decoded_chunk
                        live.update(Panel(Markdown(ai_response), title="[bold blue]Assistant[/bold blue]", border_style="blue"))

        chat_history.append({"role": "system", "content": ai_response})
        console.print(Panel(Markdown(ai_response), title="[bold blue]Assistant[/bold blue]", border_style="blue"))
