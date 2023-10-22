import typer
from rich.box import HORIZONTALS
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from .config import load_config
from .utils.brain import llm_call
from .utils.custom_inputs import multiline_input
from .utils.prompt_templates import RAG_TEMPLATE
from .utils.vectordb import (
    list_qdrant_db,
    list_remote_qdrant_db,
    qdrant_search,
    remote_qdrant_search,
)

console = Console()
config = load_config()


def search(live, user_input, sources):  # ,local_sources, remote_sources=None):
    hits = []
    local = list_qdrant_db()
    remote = list_remote_qdrant_db()

    local_sources = [source for source in sources if source in local]
    remote_sources = [source for source in sources if source in remote]

    for source_name in local_sources:
        live.update(
            Panel(
                "Searching through local sources...",
                title="[bold blue]Assistant[/bold blue]",
                border_style="blue",
            )
        )
        try:
            # Search for matches in each source based on user input
            hits.extend(qdrant_search(source_name, user_input))
        except Exception:
            # Handle potential errors with mismatched embedding models
            error_msg_local = f"Source: {source_name} was created with OpenAI's embedding model. Please run with `local_mode=False` or reindex with `mirageml delete source {source_name}; mirageml add source {source_name}`."
            error_msg_openai = f"Source: {source_name} was created with a local embedding model. Please run with `local_mode=True` or reindex with `mirageml delete source {source_name}; mirageml add source {source_name}`."

            typer.secho(
                error_msg_local if config["local_mode"] else error_msg_openai,
                fg=typer.colors.RED,
                bold=True,
            )
            return

    for source_name in remote_sources:
        live.update(
            Panel(
                "Searching through remote sources...",
                title="[bold blue]Assistant[/bold blue]",
                border_style="blue",
            )
        )
        hits.extend(remote_qdrant_search(source_name, user_input))

    return hits


def rank_hits(hits):
    # Rank the hits based on their relevance
    sorted_hits = sorted(hits, key=lambda x: x["score"], reverse=True)[:5]
    return sorted_hits


def create_context(sorted_hits):
    return "\n\n".join([str(x["payload"]["source"]) + ": " + x["payload"]["data"] for x in sorted_hits])


def search_and_rank(live, user_input, sources):
    hits = search(live, user_input, sources)
    sorted_hits = rank_hits(hits)
    return sorted_hits


def rag_chat(sources, file_and_url_context, file_and_url_sources):
    try:
        user_input = multiline_input(f"Ask a question over these sources ({', '.join(sources)})")
        if user_input.lower().strip() == "exit":
            typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
            return

        # Live display while searching for relevant sources
        with Live(
            Panel(
                "Searching through the relevant sources...",
                title="[bold blue]Assistant[/bold blue]",
                border_style="blue",
                box=HORIZONTALS,
            ),
            console=console,
            screen=False,
            auto_refresh=True,
            vertical_overflow="visible",
        ) as live:
            sorted_hits = search_and_rank(live, user_input, sources)
            sources_used = [hit["payload"]["source"] for hit in sorted_hits]
            context = create_context(sorted_hits)

            if file_and_url_context:
                context += file_and_url_context
                sources.append(file_and_url_sources)

            # Chat history that will be sent to the AI model
            chat_history = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that responds to questions concisely with the given context in the following format:\n{answer}\n\nSources:\n{sources}",
                },
                {
                    "role": "user",
                    "content": RAG_TEMPLATE.format(context=context, question=user_input, sources=sources_used),
                },
            ]

            # Fetch the AI's response
            ai_response = ""
            live.update(
                Panel(
                    "Found relevant sources! Answering question...",
                    title="[bold blue]Assistant[/bold blue]",
                    box=HORIZONTALS,
                    border_style="blue",
                )
            )
            response = llm_call(
                chat_history,
                model=config["model"],
                stream=True,
                local=config["local_mode"],
            )

            if config["local_mode"]:
                for chunk in response:
                    ai_response += chunk
                    live.update(
                        Panel(
                            Markdown(ai_response),
                            title="[bold blue]Assistant[/bold blue]",
                            box=HORIZONTALS,
                            border_style="blue",
                        )
                    )
            else:
                for chunk in response.iter_content(chunk_size=512):
                    if chunk:
                        decoded_chunk = chunk.decode("utf-8")
                        ai_response += decoded_chunk
                        live.update(
                            Panel(
                                Markdown(ai_response),
                                title="[bold blue]Assistant[/bold blue]",
                                box=HORIZONTALS,
                                border_style="blue",
                            )
                        )
            chat_history.append({"role": "assistant", "content": ai_response})
        return chat_history

    except KeyboardInterrupt:
        typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
        return
