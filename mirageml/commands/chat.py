import typer
from rich.box import HORIZONTALS
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from .config import load_config
from .list_sources import get_sources
from .rag import rag_chat
from .utils.brain import llm_call
from .utils.codeblocks import (
    add_indices_to_code_blocks,
    copy_code_to_clipboard,
    extract_code_from_markdown,
)
from .utils.custom_inputs import multiline_input

console = Console()
config = load_config()


def chat(files: list[str] = [], urls: list[str] = [], sources: list[str] = []):
    # Beginning of the chat sequence
    transient_sources = []
    if files or urls or sources:
        index_local = False
        if "local" in sources:
            index_local = True
            sources.remove("local")

        local_sources, remote_sources = get_sources()
        all_sources = list(set(local_sources + remote_sources))
        for source in sources:
            if source not in all_sources:
                typer.secho(
                    f"Source: {source} does not exist. Please add it with `mirageml add source`",
                    fg=typer.colors.RED,
                    bold=True,
                )
                sources.remove(source)

        if index_local:
            from .add_source import add_local_source

            sources.append(add_local_source("local"))

        if files or urls:
            from .utils.local_source import crawl_files
            from .utils.web_source import extract_from_url

            with Live(
                Panel(
                    "Scraping Files and Urls",
                    title="[bold green]Assistant[/bold green]",
                    border_style="green",
                ),
                console=console,
                transient=True,
            ) as live:
                for source, extractor in zip(files + urls, [crawl_files] * len(files) + [extract_from_url] * len(urls)):
                    live.update(
                        Panel(
                            f"Extracting data from {source}",
                            title="[bold green]Assistant[/bold green]",
                            border_style="green",
                        )
                    )
                    data, metadata = extractor(source)
                    transient_sources.append((data, metadata))

    while True:
        chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
        ai_response = ""
        if sources or transient_sources:
            chat_history, ai_response = rag_chat(sources, transient_sources)

        while True:
            # Loop for follow-up questions
            try:
                if ai_response:
                    code_blocks = extract_code_from_markdown(ai_response)
                    if code_blocks:
                        selected_indices = multiline_input(
                            "Enter the numbers of the code blocks you want to copy, separated by commas (e.g. '1,3,4') or ask a follow-up. Type reset to search again"
                        )
                        try:
                            selected_indices = list(map(int, selected_indices.split(",")))
                            copy_code_to_clipboard(code_blocks, selected_indices)
                            ai_response = ""
                            continue
                        except ValueError:
                            user_input = selected_indices
                else:
                    if len(chat_history) == 1:
                        user_input = multiline_input("Chat with Mirage")
                    else:
                        user_input = multiline_input("Ask a follow-up. Type reset to search again")
                if user_input.lower().strip() == "exit":
                    typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
                    return
                elif user_input.lower().strip() == "reset":
                    break

            except KeyboardInterrupt:
                typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
                return

            chat_history.append({"role": "user", "content": user_input})

            with Live(
                Panel(
                    "Assistant is thinking...",
                    title="[bold blue]Assistant[/bold blue]",
                    box=HORIZONTALS,
                    border_style="blue",
                ),
                console=console,
                transient=True,
                auto_refresh=True,
                refresh_per_second=8,
            ) as live:
                response = llm_call(
                    chat_history,
                    model=config["model"],
                    stream=True,
                    local=config["local_mode"],
                )

                ai_response = ""
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
            indexed_ai_response = add_indices_to_code_blocks(ai_response)
            console.print(
                Panel(
                    Markdown(indexed_ai_response),
                    title="[bold blue]Assistant[/bold blue]",
                    box=HORIZONTALS,
                    border_style="blue",
                )
            )
