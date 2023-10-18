import typer
import keyring
import time

from .commands import (
    login, show_config, set_config, normal_chat, rag_chat, 
    list_plugins, add_plugin, list_sources, add_source, 
    sync_plugin, delete_source
)
from .constants import SERVICE_ID, supabase

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="markdown",
    help="""
    Mirage ML CLI.

    See the website at https://mirageml.com/ for documentation and more information
    about running code on Mirage.
    """,
)

add_app = typer.Typer(name="add", help="Add a new resource", no_args_is_help=True)
list_app = typer.Typer(name="list", help="List resources", no_args_is_help=True)
sync_app = typer.Typer(name="sync", help="Sync resources", no_args_is_help=True)
delete_app = typer.Typer(name="delete", help="Delete resources", no_args_is_help=True)

app.add_typer(add_app)
app.add_typer(list_app)
app.add_typer(sync_app)
app.add_typer(delete_app)


@app.callback()
def main(ctx: typer.Context):
    user_id = keyring.get_password(SERVICE_ID, 'user_id')
    refresh_token = keyring.get_password(SERVICE_ID, 'refresh_token')
    expires_at = keyring.get_password(SERVICE_ID, 'expires_at')

    if not user_id and ctx.invoked_subcommand != "login_command":
        typer.echo("Please login first. Run `mirageml login`")
        raise typer.Exit()
    elif expires_at and float(expires_at) < time.time() and ctx.invoked_subcommand != "login_command":
        try:
            response = supabase.auth._refresh_access_token(refresh_token)
            session = response.session
            keyring.set_password(SERVICE_ID, 'access_token', session.access_token)
            keyring.set_password(SERVICE_ID, 'refresh_token', session.refresh_token)
            keyring.set_password(SERVICE_ID, 'expires_at', str(session.expires_at))
        except:
            typer.echo("Please login again. Run `mirageml login`")
            raise typer.Exit()


@app.command(name="help", hidden=True)
def custom_help():
    # Your custom help message
    typer.echo("Your Custom Help Message Here")


@app.command(name="login")
def login_command():
    """Login to Mirage ML"""
    login()


@app.command()
def chat():
    """Chat with Mirage ML"""
    normal_chat()


@app.command()
def rag(sources: list[str] = typer.Option([], '-s', '--sources', help='Sources to search for answers, specify `local` to index local files.')):
    """Chat with Mirage ML using RAG"""
    rag_chat(sources)


@list_app.command(name="plugins")
def list_plugins_command():
    """List connected plugins"""
    list_plugins()


@list_app.command(name="sources")
def list_sources_command():
    """List created sources"""
    list_sources()


@add_app.command(name="plugin")
def add_plugin_command(name: str):
    """Add a plugin by name"""
    add_plugin({"plugin": name})


@add_app.command(name="source")
def add_source_command(name: str, link: str = typer.Option("", '-l', '--link', help='Link for the source')):
    """Add a new source"""
    add_source(name, link)


@delete_app.command(name="delete")
def delete_source_command(name: str):
    """Delete a source"""
    delete_source(name)


@sync_app.command(name="sync")
def sync_plugin_command(name: str):
    """Sync a plugin"""
    sync_plugin({"plugin": name})


if __name__ == "__main__":
    app()
