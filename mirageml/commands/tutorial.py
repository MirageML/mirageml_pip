import sys
import typer
import time

def tutorial():
    from . import add_source, chat

    invoked_alias = sys.argv[0].split("/")[-1]

    typer.secho("\nGreat, you are now logged in.\n", fg=typer.colors.GREEN)

    typer.secho("Next, let's add a knowledge source for the web!", fg=typer.colors.BLUE)
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
    typer.secho("\nYou have added your first source!\n", fg=typer.colors.GREEN)

    # typer.secho("Now, let's add a plugin for additional capabilities:", fg=typer.colors.BLUE)
    # add_plugin()
    # typer.secho("\nPlugin added.\n", fg=typer.colors.GREEN)

    time.sleep(2)
    typer.secho(f"When the source is ready you can find it using `{invoked_alias} list sources` and run it with `{invoked_alias} chat -s {source_name}`", fg=typer.colors.BLUE)

    time.sleep(2)
    typer.secho(f"When chatting you can use `-f` to specify a file or directory to chat with `{invoked_alias} chat -f <file_or_directory>`", fg=typer.colors.BLUE)

    time.sleep(2)
    typer.secho(f"When chatting you can use `-u` to specify a url to chat with `{invoked_alias} chat -u <link_to_webpage>`", fg=typer.colors.BLUE)

    time.sleep(2)
    typer.secho("Let's chat with the file/directory!", fg=typer.colors.BLUE)
    file_path = input(f"Enter a file path or directory: ")

    chat([file_path])

    time.sleep(2)
    typer.secho("\nAnd that concludes the tutorial! You can now use MirageML for:", fg=typer.colors.GREEN)

    time.sleep(1)
    typer.echo("- Logging in and managing your account")

    time.sleep(1)
    typer.echo("- Adding and managing knowledge sources")

    time.sleep(1)
    typer.echo("- Adding plugins")

    time.sleep(1)
    typer.echo("- Chatting with your assistant")

    typer.secho(f"\nType '{invoked_alias} --help' for more info on all the commands.\n", fg=typer.colors.YELLOW)