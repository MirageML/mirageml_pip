import argparse
import keyring
import time

from .commands import hello, chat, login, list_plugins, add_plugin
from .constants import SERVICE_ID, supabase

def main():
    parser = argparse.ArgumentParser(description="Mirage ML CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser('hello', help='Say hello')
    subparsers.add_parser('login', help='Login to Mirage ML')
    subparsers.add_parser('chat', help='Chat with Mirage ML')

    list_parser = subparsers.add_parser('list', help='List resources')
    list_subparser = list_parser.add_subparsers(dest="subcommand")
    list_subparser.add_parser('plugins', help='List connected plugins')

    add_parser = subparsers.add_parser('add', help='Add a new resource')
    add_subparser = add_parser.add_subparsers(dest="subcommand")

    add_plugin_parser = add_subparser.add_parser('plugin', help='Name of the plugin.')
    add_plugin_parser.add_argument('name', help='Name of the plugin. Supported plugins: gdrive, notion')

    args = parser.parse_args()

    user_id = keyring.get_password(SERVICE_ID, 'user_id')
    refresh_token = keyring.get_password(SERVICE_ID, 'refresh_token')
    expires_at = keyring.get_password(SERVICE_ID, 'expires_at')

    if not user_id and args.command != "login":
        print("Please login first. Run `mirageml login`")
        return
    elif expires_at and float(expires_at) < time.time() and args.command != "login":
        try:
            response = supabase.auth._refresh_access_token(refresh_token)
            session = response.session
            keyring.set_password(SERVICE_ID, 'access_token', session.access_token)
            keyring.set_password(SERVICE_ID, 'refresh_token', session.refresh_token)
            keyring.set_password(SERVICE_ID, 'expires_at', str(session.expires_at))
        except:
            print("Please login again. Run `mirageml login`")
            return

    if args.command == "hello":
        hello()
    elif args.command == "login":
        login()
    elif args.command == "chat":
        chat()
    elif args.command == "list" and args.subcommand == "plugins":
        list_plugins()
    elif args.command == "add" and args.subcommand == "plugin":
        add_plugin({ "plugin": args.name })
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
