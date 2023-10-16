import argparse
from .commands import hello, chat, google_login, rag_question

def main():
    parser = argparse.ArgumentParser(description="mypackage CLI")
    subparsers = parser.add_subparsers(dest="command")

    login_parser = subparsers.add_parser('login', help='logs in to mirageml')
    hello_parser = subparsers.add_parser('hello', help='prints hello world')
    chat_parser = subparsers.add_parser('chat', help='Start a chat session with the bot.')
    rag_parser = subparsers.add_parser('rag', help='Start a chat session with the bot using RAG.')

    args = parser.parse_args()

    if args.command == "login":
        google_login()
    elif args.command == "hello":
        hello()
    elif args.command == "chat":
        chat()
    elif args.command == "rag":
        rag_question()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
