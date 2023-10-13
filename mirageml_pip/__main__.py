import argparse
from .commands import hello, chat, google_login

def main():
    parser = argparse.ArgumentParser(description="mypackage CLI")
    subparsers = parser.add_subparsers(dest="command")

    login_parser = subparsers.add_parser('login', help='logs in to mirageml')
    hello_parser = subparsers.add_parser('hello', help='prints hello world')
    chat_parser = subparsers.add_parser('chat', help='Start a chat session with the bot.')

    args = parser.parse_args()

    if args.command == "login":
        google_login()
    elif args.command == "hello":
        hello()
    elif args.command == "chat":
        chat()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
