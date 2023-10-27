import sys
import time
from typing import List

import typer

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="markdown",
    help="""
    MirageML CLI

    **You can use 'mirage' or 'mml' to call the package.**



    See the website at https://mirageml.com/ for documentation and more information
    about running code on MirageML.
    """,
    # pretty_exceptions_short=False, pretty_exceptions_enable=False # Needed for debugging
)

config_app = typer.Typer(name="config", help="Manage the config", no_args_is_help=True)
add_app = typer.Typer(name="add", help="Add a new resource", no_args_is_help=True)
list_app = typer.Typer(name="list", help="List resources", no_args_is_help=True)
sync_app = typer.Typer(name="sync", help="Sync resources", no_args_is_help=True)
delete_app = typer.Typer(name="delete", help="Delete resources", no_args_is_help=True)
remove_app = typer.Typer(name="remove", help="Remove resources", no_args_is_help=True)


app.add_typer(config_app, rich_help_panel="Utils and Configs")
app.add_typer(add_app, rich_help_panel="Manage Resources")
app.add_typer(list_app, rich_help_panel="Manage Resources")
app.add_typer(delete_app, rich_help_panel="Manage Resources")
app.add_typer(sync_app, rich_help_panel="Manage Resources", hidden=True)
app.add_typer(remove_app, rich_help_panel="Manage Resources", hidden=True)


@app.callback()
def main(ctx: typer.Context):
    import keyring
    import segment.analytics as analytics

    from .constants import ANALYTICS_WRITE_KEY, SERVICE_ID, fetch_new_access_token

    analytics.write_key = ANALYTICS_WRITE_KEY

    user_id = keyring.get_password(SERVICE_ID, "user_id")
    expires_at = keyring.get_password(SERVICE_ID, "expires_at")
    if not user_id and (ctx.invoked_subcommand != "login"):
        typer.echo("Please login first. Run `mirageml login`")
        raise typer.Exit()
    elif expires_at and float(expires_at) < time.time() and (ctx.invoked_subcommand != "login"):
        try:
            fetch_new_access_token()
            analytics.identify(user_id)
        except Exception:
            typer.echo("Please login again. Run `mirageml login`")
            raise typer.Exit()

    if user_id:
        full_command = " ".join(sys.argv[1:])
        analytics.track(user_id, "command", {"command": full_command})


@app.command(name="help", hidden=True)
def custom_help():
    # Your custom help message
    import os

    os.system("mml --help")


@app.command(name="login")
def login_command():
    """Login to Mirage ML"""
    from .commands import login

    login()


@app.command(name="profile", hidden=True)
def profile_command():
    """View your profile"""
    from .commands import profile

    profile()


def generate_chat_help_text():
    from .constants import help_list_sources

    return help_list_sources("chat -s")


@app.command(name="chat")
def chat_command(
    filepaths: List[str] = typer.Option(
        None,
        "--files",
        "-f",
        help="Path to files/directories to use as context. \n\n\n**"
        + sys.argv[0].split("/")[-1]
        + " chat -f {filepath} -f {directory}**",
    ),
    urls: List[str] = typer.Option(
        None,
        "--urls",
        "-u",
        help="URLs to use as context. \n\n\n**" + sys.argv[0].split("/")[-1] + " chat -u {url1} -u {url2}**",
    ),
    sources: List[str] = typer.Option(None, "--sources", "-s", help=generate_chat_help_text()),
    sp: str = typer.Option(None, "--system-prompt", "-sp", help="Name of the system prompt to use"),
):
    """Chat with MirageML"""
    for url in urls:
        if not url.startswith("http"):
            typer.echo("Every url must start with http://")
            raise typer.Exit()

    if len(urls + filepaths) > 0:
        typer.secho(
            "Indexing sources...",
            fg=typer.colors.BRIGHT_GREEN,
            bold=True,
        )
    else:
        typer.secho(
            "Starting chat. Type 'exit' to end the chat.",
            fg=typer.colors.BRIGHT_GREEN,
            bold=True,
        )

    from .commands import chat

    chat(files=filepaths, urls=urls, sources=sources, sp=sp)


@config_app.command(name="show")
def show_config_command():
    """Show the current config"""
    from .commands import show_config

    show_config()


@config_app.command(name="get", hidden=True)
def get_config_command():
    """Show the current config"""
    from .commands import show_config

    show_config()


@config_app.command(name="set")
def set_config_command():
    """
    Set the config file for MirageML
    """
    from .commands import set_config

    set_config()


# List Commands
@list_app.command(name="sp", hidden=True)
def list_system_prompts():
    from .commands import list_system_prompts

    list_system_prompts()


@list_app.command(name="plugins", hidden=True)
def list_plugins_command():
    """List connected plugins"""
    from .commands import list_plugins

    list_plugins()


@list_app.command(name="sources")
def list_sources_command():
    """List created sources"""
    from .commands import list_sources

    list_sources()


@list_app.command(name="models")
def list_models_command():
    """List created models"""
    from .commands import list_models

    list_models()


# Add Commands
@add_app.command(name="plugin", hidden=True)
def add_plugin_command(name: str):
    """Add a plugin by name"""
    from .commands import add_plugin

    add_plugin({"plugin": name})


# Add System Prompt
@add_app.command(name="sp", hidden=True)
def add_system_prompt_command(name: str = typer.Argument(default="", help="Name of the system prompt")):
    from .commands import add_system_prompt

    add_system_prompt({"name": name})


@add_app.command(name="source")
def add_source_command(link: str = typer.Argument(default="", help="Link to the source")):
    """Add a new source"""
    from .commands import add_source

    if not link.startswith("http"):
        if link:
            typer.secho("Please enter a valid link starting with https://", fg=typer.colors.RED, bold=True)
        while True:
            link = input("Link for the source: ")
            if not link.startswith("http"):
                typer.secho("Please enter a valid link starting with https://", fg=typer.colors.RED, bold=True)
                continue
            break
    from urllib.parse import urlparse

    parsed_url = urlparse(link)
    name = parsed_url.netloc.split(".")[0]
    if name in ["docs", "www", "en", "platform", "blog"]:
        name = parsed_url.netloc.split(".")[1]
    name = input(f"Name for the source [default: {name}]: ") or name
    add_source(name, link)


@add_app.command(name="sources", hidden=True)
def add_sources_command(link: str = typer.Argument(default="")):
    typer.secho("Did you mean 'add source'?", fg=typer.colors.YELLOW)
    return


@add_app.command(name="model", no_args_is_help=True)
def add_model_command(links: List[str] = typer.Argument(..., help="Links to finetune on separated by spaces\n\n\nEx: mirage add model https://modal.com https://apple.com")):
    """Add a new source"""
    from .commands import add_model

    for link in links:
        if not link.startswith("http"):
            typer.secho("Please ensure links start with https://", fg=typer.colors.RED, bold=True)
            raise typer.Exit()

    from urllib.parse import urlparse

    parsed_url = urlparse(links[0])
    name = parsed_url.netloc.split(".")[0]
    if name in ["docs", "www", "en", "platform", "blog"]:
        name = parsed_url.netloc.split(".")[1]
    name = input(f"Name for the model [default: {name}]: ") or name
    add_model(name, links)


@add_app.command(name="models", hidden=True)
def add_models_command(links: List[str] = typer.Argument(...)):
    typer.secho("Did you mean 'add model'?", fg=typer.colors.YELLOW)
    return


# Delete Commands
@delete_app.command(name="sp", hidden=True)
def delete_system_prompt(name: str = typer.Argument(default="", help="Name of the system prompt")):
    from .commands import delete_system_prompt

    delete_system_prompt({"name": name})


def generate_delete_help_text():
    from .constants import help_list_sources

    return help_list_sources("delete source")


@remove_app.command(name="source", no_args_is_help=True, hidden=True)
@delete_app.command(name="source", no_args_is_help=True)
def delete_source_command(names: List[str] = typer.Argument(help=generate_delete_help_text())):
    """Delete sources"""
    from .commands import delete_source

    delete_source(names)


# Sync Commands
@sync_app.command(name="plugin", hidden=True)
def sync_plugin_command(name: str):
    """Sync a plugin"""
    from .commands import sync_plugin

    sync_plugin({"plugin": name})


if __name__ == "__main__":
    app()
