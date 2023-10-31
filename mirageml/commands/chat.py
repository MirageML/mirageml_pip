import os

import typer
from rich import print
from rich.box import HORIZONTALS
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from .add_source import add_local_source
from .config import load_config
from .list_sources import get_sources
from .rag import rag_chat
from .utils.codeblocks import (
    add_indices_to_code_blocks,
    copy_code_to_clipboard,
    extract_code_from_markdown,
)
from .utils.custom_inputs import multiline_input
from .utils.llm import llm_call
from .utils.type_check import is_convertable_to_int

console = Console()
config = load_config()


def chat(files: list[str] = [], urls: list[str] = [], sources: list[str] = [], sp: str = ""):
    # Beginning of the chat sequence
    transient_sources = []
    if files or urls or sources:
        index_local = False
        if "local" in sources:
            index_local = True
            sources.remove("local")

        for file in files:
            if os.path.isdir(file):
                sources.append(add_local_source(file))
                files.remove(file)

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
                    if data:
                        transient_sources.append((data, metadata))

    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    while True:
        ai_response = ""
        code_blocks = []
        if sources or transient_sources:
            chat_history, ai_response = rag_chat(sources, transient_sources)

        set_sp = False
        if sp:
            new_system_prompts = list(filter(lambda x: x["name"] == sp, config["system_prompts"]))
            if len(new_system_prompts) == 0:
                typer.secho("Please enter a valid system prompt name", fg=typer.colors.RED, bold=True)
            else:
                set_sp = True
                chat_history[0]["content"] = new_system_prompts[0]["prompt"]

        while True:
            # Loop for follow-up questions
            try:
                if ai_response:
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
                    code_blocks = extract_code_from_markdown(ai_response)
                    if len(code_blocks) > 0:
                        user_input = multiline_input(
                            "Enter the number(s) of the code blocks you want to copy, separated by commas (e.g. '1,3,4') or ask a follow-up. Type reset to search again. Ctrl+C to interrupt"
                        )
                    else:
                        user_input = multiline_input("Ask a follow-up. Type reset to search again. Ctrl+C to interrupt")
                else:
                    if len(chat_history) == 1:
                        base_message = "Chat with Mirage"
                        if set_sp:
                            base_message += f" using system prompt: {sp}."
                        user_input = multiline_input(base_message)
                    elif len(code_blocks) > 0:
                        user_input = multiline_input(
                            "Enter the number(s) of the code blocks you want to copy, separated by commas (e.g. '1,3,4') or ask a follow-up. Type reset to search again. Ctrl+C to interrupt"
                        )
                    else:
                        user_input = multiline_input("Ask a follow-up. Type reset to search again. Ctrl+C to interrupt")

                if user_input.lower().strip() == "exit":
                    typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
                    return
                elif user_input.lower().strip() == "/help" or user_input.lower().strip() == "help":
                    typer.secho("Use this chat to talk to mirage", fg=typer.colors.BRIGHT_GREEN, bold=True)
                    typer.echo("'exit' to end the chat.")
                    typer.echo("'reset' to start over.")
                    typer.echo("'/help' to see this message again.")
                    typer.echo(
                        "'/copy {index}' to copy a code block to your clipboard. (Note: code block indicies start at 1)"
                    )
                    typer.echo("'/sp set {system_prompt_name}' to set the system prompt.")
                    continue
                elif is_convertable_to_int(user_input.lower().strip()) and len(code_blocks) >= int(
                    user_input.lower().strip()
                ):
                    copy_code_to_clipboard(code_blocks, [int(user_input.lower().strip())])
                    ai_response = ""
                    continue
                elif user_input.lower().strip().startswith("/copy"):
                    user_input_split = user_input.split(" ")
                    if len(code_blocks) == 0:
                        typer.secho("No code blocks to copy", fg=typer.colors.RED, bold=True)
                    elif len(user_input_split) == 1:
                        typer.secho("Please enter a code block index", fg=typer.colors.RED, bold=True)
                    elif len(user_input_split) == 2:
                        try:
                            selected_indicies = list(map(int, user_input_split[1].split(",")))
                            copy_code_to_clipboard(code_blocks, selected_indicies)
                            typer.secho("Copied code to clipboard", fg=typer.colors.BRIGHT_GREEN, bold=True)
                            ai_response = ""
                        except Exception:
                            typer.secho(
                                "Could not copy. Please enter a valid code block index", fg=typer.colors.RED, bold=True
                            )
                    continue
                elif user_input.lower().strip().startswith("/sp"):
                    user_input_split = user_input.split(" ")
                    if len(user_input_split) == 1:
                        from .list_system_prompts import list_system_prompts

                        print(f"[bold green]Current System Prompt: [/green bold]{chat_history[0]['content']}")
                        list_system_prompts()
                    elif user_input_split[1] == "set" and len(user_input_split) == 2:
                        typer.secho("Please enter a system prompt name", fg=typer.colors.RED, bold=True)
                    elif user_input_split[1] == "set" and len(user_input_split == 3):
                        system_prompt_name = user_input_split[2]
                        new_system_prompts = list(
                            filter(lambda x: x["name"] == system_prompt_name, config["system_prompts"])
                        )
                        if len(new_system_prompts) == 0:
                            typer.secho("Please enter a valid system prompt name", fg=typer.colors.RED, bold=True)
                        else:
                            chat_history[0]["content"] = new_system_prompts[0]["prompt"]
                            typer.secho(
                                f"System prompt set to {system_prompt_name}", fg=typer.colors.BRIGHT_GREEN, bold=True
                            )
                    continue
                elif (
                    user_input.lower().strip() == "reset"
                    or user_input.lower().strip() == "restart"
                    or user_input.lower().strip() == "start over"
                    or user_input.lower().strip() == "clear"
                ):
                    break

            except KeyboardInterrupt:
                typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
                return

            chat_history.append({"role": "user", "content": user_input})

            try:
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
            except KeyboardInterrupt:
                pass
