import typer
from rich.box import HORIZONTALS
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt

from .config import load_config
from .utils.brain import llm_call
from .utils.prompt_templates import CHAT_TEMPLATE


console = Console()

def normal_chat(file_path: str = None):
    # Try loading in data from file
    file_data = ""
    if file_path:
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                file_data = file_path + ": " + file_content
        except Exception as e:
            # If unable to read a file, you can print an error or continue to the next file
            typer.secho(f"Unable to read file: {file_path}", fg=typer.colors.BRIGHT_RED, bold=True)

    config = load_config()
    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]

    typer.secho("Starting chat. Type 'exit' to end the chat.", fg=typer.colors.BRIGHT_GREEN, bold=True)
    while True:
        try:
            user_input = Prompt.ask("Chat with Mirage", default="exit", show_default=False)
            if user_input.lower().strip() == 'exit':
                typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
                break
        except KeyboardInterrupt:
            typer.secho("Ending chat. Goodbye!", fg=typer.colors.BRIGHT_GREEN, bold=True)
            break

        if file_data and len(chat_history) == 1:
            user_input = CHAT_TEMPLATE.format(context=file_data, question=user_input)
        chat_history.append({"role": "user", "content": user_input})

        # Show the typing indicator using Live
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

        # Print the final AI response outside of the Live context so it persists
        chat_history.append({"role": "system", "content": ai_response})
        console.print(Panel(Markdown(ai_response), box=HORIZONTALS, title="[bold blue]Assistant[/bold blue]", border_style="blue", padding=(1, 0)))