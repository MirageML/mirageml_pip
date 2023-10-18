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


@app.command()
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


@app.command(name="list-plugins")
def list_plugins_command():
    """List connected plugins"""
    list_plugins()


@app.command(name="list-sources")
def list_sources_command():
    """List created sources"""
    list_sources()


@app.command(name="add-plugin")
def add_plugin_command(name: str):
    """Add a plugin by name"""
    add_plugin({"plugin": name})


@app.command(name="add-source")
def add_source_command(name: str, link: str = typer.Option("", '-l', '--link', help='Link for the source')):
    """Add a new source"""
    add_source(name, link)


@app.command(name="delete-source")
def delete_source_command(name: str):
    """Delete a source"""
    delete_source(name)


@app.command(name="sync-plugin")
def sync_plugin_command(name: str):
    """Sync a plugin"""
    sync_plugin({"plugin": name})


if __name__ == "__main__":
    app()


# def main():
#     parser = argparse.ArgumentParser(description="Mirage ML CLI")
#     subparsers = parser.add_subparsers(dest="command")

#     subparsers.add_parser('login', help='Login to Mirage ML')
#     subparsers.add_parser('chat', help='Chat with Mirage ML')

#     # Config Parser
#     config_parser = subparsers.add_parser('config', help='Configure Mirage ML')
#     config_subparser = config_parser.add_subparsers(dest="subcommand")
#     config_subparser.add_parser('show', help='Show current configuration')
#     config_subparser.add_parser('set', help='Set configuration')

#     # RAG Parser
#     rag_parser = subparsers.add_parser('rag', help='Chat with Mirage ML using RAG')
#     rag_parser.add_argument('-s', '--sources', nargs='+', default=[],
#                             help='Sources to search for answers, specify `local` to index local files.')

#     # List Parser
#     list_parser = subparsers.add_parser('list', help='List resources')
#     list_subparser = list_parser.add_subparsers(dest="subcommand")
#     list_subparser.add_parser('plugins', help='List connected plugins')
#     list_subparser.add_parser('sources', help='List created sources')

#     # Add Parser
#     add_parser = subparsers.add_parser('add', help='Add a new resource')
#     add_subparser = add_parser.add_subparsers(dest="subcommand")
#     ## Add Plugin
#     add_plugin_parser = add_subparser.add_parser('plugin', help='Name of the plugin.')
#     add_plugin_parser.add_argument('name', help='Name of the plugin. Supported plugins: notion')
#     ## Add Source
#     add_source_parser = add_subparser.add_parser('source', help='Add a new source, if no link is specified, the current directory is added as a source.')
#     add_source_parser.add_argument('name', help='Name of the source')
#     add_source_parser.add_argument('-l', '--link', help='Link for the source')

#     # Delete Parser
#     delete_parser = subparsers.add_parser('delete', help='delete a new resource')
#     delete_subparser = delete_parser.add_subparsers(dest="subcommand")
#     ## Delete Source
#     delete_source_parser = delete_subparser.add_parser('source', help='delete a new source')
#     delete_source_parser.add_argument('name', help='Name of the source')

#     # Sync Parser
#     sync_parser = subparsers.add_parser('sync', help='Sync resources')
#     sync_subparser = sync_parser.add_subparsers(dest="subcommand")
#     ## Sync Plugin
#     sync_plugin_parser = sync_subparser.add_parser('plugin', help='Sync a plugin')
#     sync_plugin_parser.add_argument('name', help='Name of the plugin. Supported plugins: notion')

#     args = parser.parse_args()

#     user_id = keyring.get_password(SERVICE_ID, 'user_id')
#     refresh_token = keyring.get_password(SERVICE_ID, 'refresh_token')
#     expires_at = keyring.get_password(SERVICE_ID, 'expires_at')

#     if not user_id and args.command != "login":
#         print("Please login first. Run `mirageml login`")
#         return
#     elif expires_at and float(expires_at) < time.time() and args.command != "login":
#         try:
#             response = supabase.auth._refresh_access_token(refresh_token)
#             session = response.session
#             keyring.set_password(SERVICE_ID, 'access_token', session.access_token)
#             keyring.set_password(SERVICE_ID, 'refresh_token', session.refresh_token)
#             keyring.set_password(SERVICE_ID, 'expires_at', str(session.expires_at))
#         except:
#             print("Please login again. Run `mirageml login`")
#             return

#     if args.command == "login":
#         login()
#     elif args.command == "config":
#         if args.subcommand == "show":
#             show_config()
#         elif args.subcommand == "set":
#             set_config()
#         else:
#             config_parser.print_help()
#     elif args.command == "chat":
#         chat()
#     elif args.command == "rag":
#         rag(args.sources)
#     elif args.command == "list":
#         if args.subcommand == "plugins":
#             list_plugins()
#         elif args.subcommand == "sources":
#             list_sources()
#         else:
#             list_parser.print_help()
#     elif args.command == "add":
#         if args.subcommand == "plugin":
#             add_plugin({ "plugin": args.name })
#         elif args.subcommand == "source":
#             add_source(args)
#         else:
#             add_parser.print_help()
#     elif args.command == "delete":
#         if args.subcommand == "source":
#             delete_source(args)
#         else:
#             delete_parser.print_help()
#     elif args.command == "sync" and args.subcommand == "plugin":
#         sync_plugin({ "plugin": args.name })
#     else:
#         parser.print_help()

# if __name__ == "__main__":
#     main()
