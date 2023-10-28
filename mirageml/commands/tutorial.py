import sys
import time

import typer


def tutorial():
    from . import add_source, chat

    invoked_alias = sys.argv[0].split("/")[-1]

    typer.secho("\nGreat, you are now logged in.\n", fg=typer.colors.BRIGHT_GREEN)

    typer.secho(
        "Next, let's add a knowledge source for the web (ex: https://modal.com/docs)!", fg=typer.colors.BRIGHT_BLUE
    )
    while True:
        link = input("Link for the source: ")
        if not link.startswith("http"):
            typer.secho("Please enter a valid link starting with https://", fg=typer.colors.RED, bold=True)
            continue
        break
    from urllib.parse import urlparse

    parsed_url = urlparse(link)
    source_name = parsed_url.netloc.split(".")[0]
    if source_name in ["docs", "www", "en", "platform", "blog"]:
        source_name = parsed_url.netloc.split(".")[1]
    source_name = input(f"source_name for the source [default: {source_name}]: ") or source_name
    add_source(source_name, link)

    time.sleep(2)
    typer.secho("\nYou have added your first source!", fg=typer.colors.BRIGHT_GREEN)

    # typer.secho("Now, let's add a plugin for additional capabilities:", fg=typer.colors.BRIGHT_BLUE)
    # add_plugin()
    # typer.secho("\nPlugin added.\n", fg=typer.colors.BRIGHT_GREEN)

    time.sleep(2)
    typer.secho(
        f"Use `{invoked_alias} chat -s modal` when your source is ready and `{invoked_alias} list sources` to list your sources\n",
        fg=typer.colors.BRIGHT_GREEN,
    )

    time.sleep(2)
    typer.secho(
        f"Use `{invoked_alias} chat -u <link_to_webpage>` to open a chat over a specific url",
        fg=typer.colors.BRIGHT_BLUE,
    )

    time.sleep(2)
    typer.secho(
        f"Use `{invoked_alias} chat -f <file_or_directory>` to open a chat over a file or directory",
        fg=typer.colors.BRIGHT_BLUE,
    )

    time.sleep(2)
    typer.secho("Let's chat with a file or directory!", fg=typer.colors.BRIGHT_BLUE)

    from prompt_toolkit import prompt
    from prompt_toolkit.completion import PathCompleter

    file_path = prompt("Enter the filepath to a file or directory: ", completer=PathCompleter())

    chat([file_path])

    time.sleep(2)
    typer.secho("\nAnd that concludes the tutorial! You can now use MirageML for:", fg=typer.colors.BRIGHT_GREEN)

    time.sleep(1)
    typer.echo("- Logging in and managing your account")

    time.sleep(1)
    typer.echo("- Adding and managing knowledge sources")

    time.sleep(1)
    typer.echo("- Finetuning a custom model")

    time.sleep(1)
    typer.echo("- Adding plugins")

    time.sleep(1)
    typer.echo("- Chatting with your context-aware assistant")

    typer.secho(f"\nType `{invoked_alias} --help` for more info on all the commands.\n", fg=typer.colors.YELLOW)
