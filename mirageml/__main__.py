import sys
import time
import typer
from typing import List

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
)

config_app = typer.Typer(name="config", help="Manage the config", no_args_is_help=True)
add_app = typer.Typer(name="add", help="Add a new resource", no_args_is_help=True)
list_app = typer.Typer(name="list", help="List resources", no_args_is_help=True)
sync_app = typer.Typer(name="sync", help="Sync resources", no_args_is_help=True)
delete_app = typer.Typer(name="delete", help="Delete resources", no_args_is_help=True)

app.add_typer(config_app, rich_help_panel="Utils and Configs")
app.add_typer(add_app, rich_help_panel="Manage Resources")
app.add_typer(list_app, rich_help_panel="Manage Resources")
app.add_typer(sync_app, rich_help_panel="Manage Resources")
app.add_typer(delete_app, rich_help_panel="Manage Resources")


@app.callback()
def main(ctx: typer.Context):
    import keyring
    from .constants import SERVICE_ID, ANALYTICS_WRITE_KEY, fetch_new_access_token
    import segment.analytics as analytics

    analytics.write_key = ANALYTICS_WRITE_KEY

    user_id = keyring.get_password(SERVICE_ID, 'user_id')
    expires_at = keyring.get_password(SERVICE_ID, 'expires_at')
    if not user_id and ctx.invoked_subcommand != "login":
        typer.echo("Please login first. Run `mirageml login`")
        raise typer.Exit()
    elif expires_at and float(expires_at) < time.time() and ctx.invoked_subcommand != "login":
        try:
            fetch_new_access_token()
            analytics.identify(user_id)
        except:
            typer.echo("Please login again. Run `mirageml login`")
            raise typer.Exit()

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


def generate_help_text():
    from .constants import help_list_sources
    return help_list_sources()

@app.command()
def chat(
        file_or_url: str = typer.Option(None, "--file-or-url", "-f", help="Path to a file or URL to use as context. \n\n\n**"+sys.argv[0].split('/')[-1]+" chat -f {filepath_or_url}**"),
        sources: List[str] = typer.Option([], "--sources", "-s", help=generate_help_text())
    ):
    """Chat with MirageML"""
    typer.secho("Starting chat. Type 'exit' to end the chat.", fg=typer.colors.BRIGHT_GREEN, bold=True)
    if sources:
        from .commands import rag_chat
        rag_chat(file_or_url, sources)
    else:
        from .commands import normal_chat
        normal_chat(file_or_url=file_or_url)


@config_app.command(name="show")
def show_config_command():
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
@list_app.command(name="plugins")
def list_plugins_command():
    """List connected plugins"""
    from .commands import list_plugins
    list_plugins()


@list_app.command(name="sources")
def list_sources_command():
    """List created sources"""
    from .commands import list_sources
    list_sources()


# Add Commands
@add_app.command(name="plugin")
def add_plugin_command(name: str):
    """Add a plugin by name"""
    from .commands import add_plugin
    add_plugin({"plugin": name})


@add_app.command(name="source")
def add_source_command():
    """Add a new source"""
    from .commands import add_source
    while True:
        link = input("Link for the source: ")
        if not link.startswith("https://"):
            typer.echo("Please enter a valid link starting with https://")
            continue
        break
    from urllib.parse import urlparse
    parsed_url = urlparse(link)
    name = parsed_url.netloc.split('.')[0]
    if name == "docs": name = parsed_url.netloc.split('.')[1]
    name = input(f"Name for the source [default: {name}]: ") or name
    add_source(name, link)


# Delete Commands
@delete_app.command(name="source")
def delete_source_command(name: str = typer.Argument(default="", help="Name of the source to delete")):
    """Delete a source"""
    from .commands import delete_source
    delete_source(name)


# Sync Commands
@sync_app.command(name="plugin")
def sync_plugin_command(name: str):
    """Sync a plugin"""
    from .commands import sync_plugin
    sync_plugin({"plugin": name})


if __name__ == "__main__":
    app()
