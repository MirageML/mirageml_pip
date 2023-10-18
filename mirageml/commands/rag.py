import os
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
import typer

from .config import load_config
from .utils.brain import get_embedding, llm_call
from .utils.vectordb import get_qdrant_db
from .add_source import add_local_source

console = Console()

def rag_chat(sources: list = None):
    config = load_config()
    if not sources:
        typer.secho("By default Mirage will index the files under the current directory.", fg=typer.colors.RED, bold=True)
        typer.secho("If you want to run RAG over other sources, please specify them with `--sources`.", fg=typer.colors.BRIGHT_RED, bold=True)
        user_input = Prompt.ask("If you'd like to proceed type 'yes'", default="yes", show_default=True)
        user_input = input(": ")
        if user_input.lower().startswith("y"):
            sources = ["local"]
        else: return

    if "local" in sources:
        sources.remove("local")
        sources.append(add_local_source())

    qdrant_client = get_qdrant_db()

    template = """Answer the question based only on the following context, if the context isn't relevant answer without it. If the context is relevant, mention which sources you used.:
    {context}

    Sources:
    {sources}

    Question: {question}
    """

    typer.secho("Starting chat. Type 'exit' to end the chat.", fg=typer.colors.BRIGHT_GREEN, bold=True)
    user_input = Prompt.ask(f"Chat with Mirage ({', '.join(sources)})", default="exit", show_default=False)

    hits = []
    for source_name in sources:
        try:
            hits.extend(qdrant_client.search(
                collection_name=source_name,
                query_vector=get_embedding([user_input], local=config["local_mode"])[0],
                limit=5
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

    chat_history = [
        {"role": "system", "content": "You are a helpful assistant that responds to questions concisely with the given context in the following format:\n{answer}\n\nSources:\n{sources}"},
        {"role": "user", "content": template.format(context=context, question=user_input, sources=sources)}
    ]

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
