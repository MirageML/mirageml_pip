import re
import typer
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt

from .config import load_config
from .add_source import add_local_source
from .utils.brain import get_embedding, llm_call
from .utils.vectordb import get_qdrant_db, list_qdrant_db

from .utils.prompt_templates import RAG_TEMPLATE

console = Console()

def rag_chat():
    config = load_config()

    possible_sources = list_qdrant_db() + ["local"]

    # Give the user a list of possible sources and ask them to choose which ones to use, also add local as an option
    while True:
        typer.secho("Here are the possible sources you can use:", fg=typer.colors.BRIGHT_GREEN, bold=True)
        for source in possible_sources:
            typer.secho(f" - {source}", fg=typer.colors.GREEN, bold=True)
        sources_input = Prompt.ask("Which sources would you like to use? (separate multiple sources with a space or comma)", default="local", show_choices=True, show_default=True)
        sources = [source.strip() for source in re.split(',|\s+', sources_input) if source.strip()]

        invalid_sources = [source for source in sources if source not in possible_sources]
        if invalid_sources:
            for source in invalid_sources:
                typer.secho(f"Invalid source: {source}", fg=typer.colors.BRIGHT_RED, bold=True)
            continue
        else:
            break

    if not sources:
        typer.secho("By default Mirage will index the files under the current directory.", fg=typer.colors.RED, bold=True)
        typer.secho("If you want to run RAG over other sources, please specify them with `--sources`.", fg=typer.colors.BRIGHT_RED, bold=True)
        user_input = Prompt.ask("If you'd like to proceed type 'yes'", default="yes", show_default=True)
        if user_input.lower().startswith("y"):
            sources = ["local"]
        else: return

    if "local" in sources:
        sources.remove("local")
        sources.append(add_local_source())

    qdrant_client = get_qdrant_db()

    # Start the chat
    user_input = Prompt.ask(f"Chat with Mirage ({', '.join(sources)})", default="exit", show_default=False)

    with Live(Panel("Searching for the relevant sources...",
                title="[bold blue]Assistant[/bold blue]", border_style="blue"),
                console=console, screen=True, auto_refresh=True, vertical_overflow="visible") as live:

        hits = []
        for source_name in sources:
            try:
                hits.extend(qdrant_client.search(
                    limit=5,
                    collection_name=source_name,
                    query_vector=get_embedding([user_input], local=config["local_mode"])[0],
                ))
            except:
                if config["local_mode"]:
                    typer.secho(f"Source: {source_name} was created with OpenAI's embedding model. Please run with `local_mode=False` or reindex with `mirageml delete source {source_name}; mirageml add source {source_name}`.", fg=typer.colors.RED, bold=True)
                    return
                else:
                    typer.secho(f"Source: {source_name} was created with a local embedding model. Please run with `local_mode=True` or reindex with `mirageml delete source {source_name}; mirageml add source {source_name}`.", fg=typer.colors.RED, bold=True)
                    return

        sorted_hits = sorted(hits, key=lambda x: x.score, reverse=True)[:10]
        sources = "\n".join([str(x.payload["source"]) for x in sorted_hits])
        context = "\n\n".join([str(x.payload["source"]) + ": " + x.payload["data"] for x in sorted_hits])

        live.update(Panel("Found relevant sources! Answering question...", title="[bold blue]Assistant[/bold blue]", border_style="blue"))

        chat_history = [
            {"role": "system", "content": "You are a helpful assistant that responds to questions concisely with the given context in the following format:\n{answer}\n\nSources:\n{sources}"},
            {"role": "user", "content": RAG_TEMPLATE.format(context=context, question=user_input, sources=sources)}
        ]

    ai_response = ""
    ai_response = ""
    with Live(Panel("Found relevant sources! Answering question...", title="[bold blue]Assistant[/bold blue]", border_style="blue"),
                  console=console, screen=True, auto_refresh=True, vertical_overflow="visible") as live:
        ai_response = ""
    with Live(Panel("Found relevant sources! Answering question...", title="[bold blue]Assistant[/bold blue]", border_style="blue"),
                  console=console, screen=True, auto_refresh=True, vertical_overflow="visible") as live:
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

    chat_history.append({"role": "system", "content": ai_response})
    console.print(Panel(Markdown(ai_response), title="[bold blue]Assistant[/bold blue]", border_style="blue"))

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
