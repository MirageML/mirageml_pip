import typer

from mirageml.classes import LoginManager
from mirageml.constants import REDIRECT_URI


def add_gdrive():
    m = LoginManager(
        handler="google_auth_handler",
        provider="google",
        provider_options={
            "redirect_to": REDIRECT_URI,
            "scopes": "https://www.googleapis.com/auth/drive",
            "query_params": {
                "access_type": "offline",
                "prompt": "consent",
            },
        },
    )
    m.start_web_server()
    m.open_browser()


def add_notion():
    m = LoginManager(
        handler="notion_auth_handler",
        provider="notion",
        provider_options={
            "redirect_to": REDIRECT_URI,
        },
    )
    m.start_web_server()
    m.open_browser()

def add_linear():
    m = LoginManager(
        handler="linear_auth_handler",
        provider="linear",
        provider_options={
            "redirect_to": REDIRECT_URI,
        },
    )
    m.start_web_server()
    m.open_browser()


def add_plugin(args):
    plugin_name = args["plugin"]
    if plugin_name == "notion":
        add_notion()
    elif plugin_name == "linear":
        add_linear()
    # elif plugin_name == "gdrive":
    #     add_gdrive()
    else:
        typer.secho(
            "Only notion plugin is supported for now.",
            fg=typer.colors.BRIGHT_RED,
            bold=True,
        )
