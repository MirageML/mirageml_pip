import os
import typer
from rich.box import HORIZONTALS
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt

from .config import load_config
from .rag import rag_chat
from .utils.codeblocks import extract_code_from_markdown, add_indices_to_code_blocks, copy_code_to_clipboard
from .utils.custom_inputs import multiline_input
from .utils.brain import llm_call
from .utils.prompt_templates import CHAT_TEMPLATE

console = Console()
config = load_config()

def chat(files: list[str] = [], urls: list[str] = [], sources: list[str] = []):
    # Beginning of the chat sequence
    file_and_url_sources, file_and_url_context = [], ""
    local_sources = []

    with Live(Panel("Getting ready...", title="[bold blue]Assistant[/bold blue]", border_style="blue"),
                        console=console, transient=True, auto_refresh=True, refresh_per_second=8) as live:

        if "local" in sources:
            local_sources = ["local"]
            sources.remove("local")

        for file in files:
            from .utils.local_source import extract_from_file
            # Check if filepath is a directory and is valid
            if os.path.exists(file) and os.path.isdir(file):
                local_sources.append(file)
            else:
                live.update(Panel("Extracting files...", title="[bold blue]Assistant[/bold blue]", border_style="blue"))
                source, file_data = extract_from_file(file, live)
                file_and_url_sources.append(source)
                file_and_url_context += "\n\n" + source + ": " + file_data

        for url in urls:
            from .utils.web_source import extract_from_url
            live.update(Panel("Scraping URLs...", title="[bold blue]Assistant[/bold blue]", border_style="blue"))
            source, url_data = extract_from_url(url, live)
            file_and_url_sources.append(source)
            file_and_url_context += "\n\n" + source + ": " + url_data

    for dir_path in local_sources:
        from .add_source import add_local_source
        sources.append(add_local_source(dir_path))

    while True:
        chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
        ai_response = ""
        if sources:
            chat_history = rag_chat(sources, file_and_url_context, file_and_url_sources)

        while True:
            # Loop for follow-up questions
            try:
                code_blocks = extract_code_from_markdown(ai_response)
                if code_blocks:
                    selected_indices = multiline_input("Enter the numbers of the code blocks you want to copy, separated by commas (e.g. '1,3,4') or ask a follow-up. Type reset to search again")
                    try:
                        selected_indices = list(map(int, selected_indices.split(',')))
                        copy_code_to_clipboard(code_blocks, selected_indices)
                        ai_response = ""
                        continue
                    except ValueError: user_input = selected_indices
                else:
                    if len(chat_history) == 1 and len(file_and_url_sources):
                        user_input = multiline_input(f"Ask a question over these sources ({', '.join(file_and_url_sources)})")
                    elif len(chat_history) == 1: user_input = multiline_input("Chat with Mirage")
                    else: user_input = multiline_input("Ask a follow-up. Type reset to search again")
                if user_input.lower().strip() == 'exit':
                    typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
                    return
                elif user_input.lower().strip() == 'reset':
                    break

                if file_and_url_context and len(chat_history) == 1:
                    user_input = CHAT_TEMPLATE.format(context=file_and_url_context, question=user_input)

                chat_history.append({"role": "user", "content": user_input})

                with Live(Panel("Assistant is thinking...", title="[bold blue]Assistant[/bold blue]", box=HORIZONTALS, border_style="blue"),
                        console=console, transient=True, auto_refresh=True, refresh_per_second=8) as live:

                    response = llm_call(chat_history, model=config["model"], stream=True, local=config["local_mode"])

                    ai_response = ""
                    if config["local_mode"]:
                        for chunk in response:
                            ai_response += chunk
                            live.update(Panel(Markdown(ai_response), title="[bold blue]Assistant[/bold blue]", box=HORIZONTALS, border_style="blue"))
                    else:
                        for chunk in response.iter_content(chunk_size=512):
                            if chunk:
                                decoded_chunk = chunk.decode('utf-8')
                                ai_response += decoded_chunk
                                live.update(Panel(Markdown(ai_response), title="[bold blue]Assistant[/bold blue]", box=HORIZONTALS, border_style="blue"))

                chat_history.append({"role": "assistant", "content": ai_response})
                indexed_ai_response = add_indices_to_code_blocks(ai_response)
                console.print(Panel(Markdown(indexed_ai_response), title="[bold blue]Assistant[/bold blue]", box=HORIZONTALS, border_style="blue"))

            except KeyboardInterrupt:
                typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
                return
